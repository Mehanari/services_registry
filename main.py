from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import mysql.connector
from mysql.connector import Error


# ------------------------ Pydantic Models ------------------------

class Service(BaseModel):
    id: int
    name: str
    version: str
    url: str
    description: str


class ServiceView(BaseModel):
    id: int
    name: str
    version: str
    description: str


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
            database="services_registry"
        )
        return connection
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")


# ------------------------ FastAPI App ------------------------

app = FastAPI()


@app.post("/services/", response_model=Service)
def add_service(service: Service):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO service (name, version, url, description) VALUES (%s, %s, %s, %s)",
            (service.name, service.version, service.url, service.description)
        )
        connection.commit()
        service.id = cursor.lastrowid
        return service
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to add service: {str(e)}")
    finally:
        cursor.close()
        connection.close()


@app.put("/services/{service_id}", response_model=Service)
def update_service(service_id: int, service: Service):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "UPDATE service SET name = %s, version = %s, url = %s, description = %s WHERE id = %s",
            (service.name, service.version, service.url, service.description, service_id)
        )
        connection.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Service not found")
        service.id = service_id
        return service
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to update service: {str(e)}")
    finally:
        cursor.close()
        connection.close()


@app.get("/services/", response_model=List[ServiceView])
def get_all_services():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, name, version, description FROM service")
        services = cursor.fetchall()
        return [ServiceView(**service) for service in services]
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
            "SELECT id, url FROM service WHERE name = %s AND version = %s",
            (name, version)
        )
        service = cursor.fetchone()
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")

        # Update last_activity table
        cursor.execute(
            "INSERT INTO last_activity (service_id, last_activity_time) VALUES (%s, %s) "
            "ON DUPLICATE KEY UPDATE last_activity_time = %s",
            (service["id"], datetime.utcnow(), datetime.utcnow())
        )
        connection.commit()
        return service["url"]
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch service address: {str(e)}")
    finally:
        cursor.close()
        connection.close()


@app.delete("/services/{service_id}", response_model=dict)
def delete_service(service_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM service WHERE id = %s", (service_id,))
        connection.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Service not found")
        return {"message": "Service deleted successfully"}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete service: {str(e)}")
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
