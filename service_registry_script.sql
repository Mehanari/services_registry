-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema services_registry
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `services_registry` ;

-- -----------------------------------------------------
-- Schema services_registry
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `services_registry` DEFAULT CHARACTER SET utf8 ;
USE `services_registry` ;

-- -----------------------------------------------------
-- Table `services_registry`.`version_tag`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `services_registry`.`version_tag` ;

CREATE TABLE IF NOT EXISTS `services_registry`.`version_tag` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `tag_name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `services_registry`.`service_status`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `services_registry`.`service_status` ;

CREATE TABLE IF NOT EXISTS `services_registry`.`service_status` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `status_name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `services_registry`.`service`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `services_registry`.`service` ;

CREATE TABLE IF NOT EXISTS `services_registry`.`service` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(250) NOT NULL,
  `version` VARCHAR(45) NOT NULL,
  `app_url` TEXT NOT NULL,
  `description` TEXT NOT NULL,
  `health_check_url` TEXT NOT NULL,
  `last_start_time` DATETIME NULL,
  `last_stop_time` DATETIME NULL,
  `service_status_id` INT NOT NULL,
  `version_tag_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_service_service_status`
    FOREIGN KEY (`service_status_id`)
    REFERENCES `services_registry`.`service_status` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_service_version_tag1`
    FOREIGN KEY (`version_tag_id`)
    REFERENCES `services_registry`.`version_tag` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE INDEX `fk_service_service_status_idx` ON `services_registry`.`service` (`service_status_id` ASC) VISIBLE;

CREATE INDEX `fk_service_version_tag1_idx` ON `services_registry`.`service` (`version_tag_id` ASC) VISIBLE;

CREATE UNIQUE INDEX `name_version_unique` ON `services_registry`.`service` (`name` ASC, `version` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `services_registry`.`last_activity`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `services_registry`.`last_activity` ;

CREATE TABLE IF NOT EXISTS `services_registry`.`last_activity` (
  `service_id` INT NOT NULL,
  `last_activity_time` DATETIME NOT NULL,
  PRIMARY KEY (`service_id`),
  CONSTRAINT `fk_last_activity_service1`
    FOREIGN KEY (`service_id`)
    REFERENCES `services_registry`.`service` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE INDEX `fk_last_activity_service1_idx` ON `services_registry`.`last_activity` (`service_id` ASC) VISIBLE;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
