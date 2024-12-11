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
-- Table `services_registry`.`service`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `services_registry`.`service` ;

CREATE TABLE IF NOT EXISTS `services_registry`.`service` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  `version` VARCHAR(45) NOT NULL,
  `url` TEXT NOT NULL,
  `description` TEXT NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

CREATE UNIQUE INDEX `UNIQUE_NAME_VERSION` ON `services_registry`.`service` (`version` ASC, `name` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `services_registry`.`last_activity`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `services_registry`.`last_activity` ;

CREATE TABLE IF NOT EXISTS `services_registry`.`last_activity` (
  `service_id` INT NOT NULL,
  `last_activity_time` TIMESTAMP NOT NULL,
  PRIMARY KEY (`service_id`),
  CONSTRAINT `fk_last_activity_service`
    FOREIGN KEY (`service_id`)
    REFERENCES `services_registry`.`service` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE INDEX `fk_last_activity_service_idx` ON `services_registry`.`last_activity` (`service_id` ASC) VISIBLE;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
