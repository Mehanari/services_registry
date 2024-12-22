from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import time
import mysql.connector
from mysql.connector import Error


# ------------------------ Pydantic Models ------------------------

class ServiceInfo(BaseModel):
    name: str
    version: str
    app_url: str
    description: str
    health_check_url: str
    version_tag: str


class Service(BaseModel):
    id: int
    name: str
    version: str
    app_url: str
    description: str
    health_check_url: str
    last_start_time: Optional[datetime] = None
    last_stop_time: Optional[datetime] = None
    service_status: str
    version_tag: str


class LastActivity(BaseModel):
    service_id: int
    last_activity_time: datetime


# ------------------------ Database Connection ------------------------

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="services_registry",
        )
        return connection
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")


# ------------------------ FastAPI App ------------------------

app = FastAPI()


@app.post("/services/", response_model=Service)
def add_service(service_info: ServiceInfo):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        # Get version_tag_id
        version_tag = get_version_tag_id(cursor, service_info.version_tag)

        # Insert service with default status DOWN
        cursor.execute(
            """
            INSERT INTO service (name, version, app_url, description, 
            health_check_url, service_status_id, version_tag_id)
            VALUES (%s, %s, %s, %s, %s, (SELECT id FROM service_status WHERE status_name = 'DOWN'), %s)
            """,
            (service_info.name, service_info.version, service_info.app_url,
             service_info.description, service_info.health_check_url, version_tag)
        )
        connection.commit()
        service_id = cursor.lastrowid

        # Retrieve inserted service
        cursor.execute(
            """
            SELECT s.id, s.name, s.version, s.app_url, s.description,
             s.health_check_url, ss.status_name AS service_status, vt.tag_name AS version_tag
            FROM service s
            JOIN service_status ss ON s.service_status_id = ss.id
            JOIN version_tag vt ON s.version_tag_id = vt.id
            WHERE s.id = %s
            """,
            (service_id,)
        )
        result = cursor.fetchone()
        added_service = Service(**result)
        return added_service
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to add service: {str(e)}")
    finally:
        cursor.close()
        connection.close()


@app.put("/services/{service_id}", response_model=Service)
def update_service(service_id: int, service_info: ServiceInfo):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        # Get version_tag_id
        version_tag = get_version_tag_id(cursor, service_info.version_tag)

        # Update service
        cursor.execute(
            """
            UPDATE service
            SET name = %s, version = %s, app_url = %s, description = %s, health_check_url = %s, version_tag_id = %s
            WHERE id = %s
            """,
            (service_info.name, service_info.version, service_info.app_url,
             service_info.description, service_info.health_check_url, version_tag, service_id)
        )
        connection.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Service not found")

        # Retrieve updated service
        cursor.execute(
            """
            SELECT s.id, s.name, s.version, s.app_url, s.description, 
            s.health_check_url, ss.status_name AS service_status, vt.tag_name AS version_tag
            FROM service s
            JOIN service_status ss ON s.service_status_id = ss.id
            JOIN version_tag vt ON s.version_tag_id = vt.id
            WHERE s.id = %s
            """,
            (service_id,)
        )
        result = cursor.fetchone()
        return Service(**result)
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to update service: {str(e)}")
    finally:
        cursor.close()
        connection.close()


def get_version_tag_id(cursor, version_tag):
    cursor.execute("SELECT id FROM version_tag WHERE tag_name = %s", (version_tag,))
    version_tag = cursor.fetchone()
    if not version_tag:
        raise HTTPException(status_code=400, detail="Invalid version tag")
    return version_tag["id"]


@app.get("/services/", response_model=List[Service])
def get_all_services():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT s.id, s.name, s.version, s.app_url, s.description, s.health_check_url,
             ss.status_name AS service_status, vt.tag_name AS version_tag
            FROM service s
            JOIN service_status ss ON s.service_status_id = ss.id
            JOIN version_tag vt ON s.version_tag_id = vt.id
            """
        )
        services = cursor.fetchall()
        return [Service(**service) for service in services]
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch services: {str(e)}")
    finally:
        cursor.close()
        connection.close()


@app.get("/services/address", response_model=str)
def get_service_address(name: str, version: str):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT app_url FROM service WHERE name = %s AND version = %s",
            (name, version)
        )
        service = cursor.fetchone()
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        return service["app_url"]
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch service address: {str(e)}")
    finally:
        cursor.close()
        connection.close()


@app.delete("/services/{name}/{version}", response_model=dict)
def delete_service(name: str, version: str):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "DELETE FROM service WHERE name = %s AND version = %s",
            (name, version)
        )
        connection.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Service not found")
        return {"message": "Service deleted successfully"}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete service: {str(e)}")
    finally:
        cursor.close()
        connection.close()


@app.put("/services/start/{name}/{version}", response_model=dict)
def start_service(name: str, version: str):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        current_date_time = datetime.utcnow()
        current_date_time_str = current_date_time.strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            """
            UPDATE service
            SET service_status_id = (SELECT id FROM service_status WHERE status_name = 'UP'),
                last_start_time = %s
            WHERE name = %s AND version = %s
            """,
            (current_date_time_str, name, version)
        )
        connection.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Service not found")
        return {"message": "Service started successfully"}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to start service: {str(e)}")
    finally:
        cursor.close()
        connection.close()


@app.put("/services/stop/{name}/{version}", response_model=dict)
def stop_service(name: str, version: str):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        current_date_time = datetime.utcnow()
        current_date_time_str = current_date_time.strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            """
            UPDATE service
            SET service_status_id = (SELECT id FROM service_status WHERE status_name = 'DOWN'),
                last_stop_time = %s
            WHERE name = %s AND version = %s
            """,
            (current_date_time_str, name, version)
        )
        connection.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Service not found")
        return {"message": "Service stopped successfully"}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop service: {str(e)}")
    finally:
        cursor.close()
        connection.close()


@app.post("/services/activity/{name}/{version}", response_model=dict)
def add_last_activity(name: str, version: str):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT id FROM service WHERE name = %s AND version = %s",
            (name, version)
        )
        service = cursor.fetchone()
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")

        cursor.execute(
            """
            INSERT INTO last_activity (service_id, last_activity_time)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE last_activity_time = VALUES(last_activity_time)
            """,
            (service[0], datetime.utcnow())
        )
        connection.commit()
        return {"message": "Last activity updated successfully"}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to add last activity: {str(e)}")
    finally:
        cursor.close()
        connection.close()


@app.get("/services/last_activity", response_model=List[LastActivity])
def get_last_activity():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT service_id, last_activity_time FROM last_activity")
        activities = cursor.fetchall()
        return [LastActivity(**activity) for activity in activities]
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch last activities: {str(e)}")
    finally:
        cursor.close()
        connection.close()
