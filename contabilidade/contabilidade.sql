-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema dinheiro
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema dinheiro
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `dinheiro` DEFAULT CHARACTER SET utf8 ;
USE `dinheiro` ;

-- -----------------------------------------------------
-- Table `dinheiro`.`tblContas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `dinheiro`.`tblContas` (
  `idConta` INT NOT NULL,
  `tipoConta` ENUM('C', 'D') NOT NULL,
  `nomConta` VARCHAR(50) NOT NULL,
  `criado` DATE NOT NULL,
  `modificado` DATE NOT NULL,
  `status` ENUM('A', 'I') NOT NULL DEFAULT 'A',
  PRIMARY KEY (`idConta`, `tipoConta`))
ENGINE = InnoDB;

CREATE INDEX `idxConta` ON `dinheiro`.`tblContas` (`nomConta` ASC, `tipoConta` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `dinheiro`.`tblNotas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `dinheiro`.`tblNotas` (
  `idNotas` INT NOT NULL AUTO_INCREMENT,
  `dataNota` DATE NOT NULL,
  `valor` DECIMAL(9,2) NOT NULL,
  `imprimir` ENUM('S', 'N') NOT NULL DEFAULT 'S',
  `criado` DATE NOT NULL,
  `modificado` DATE NOT NULL,
  `status` ENUM('A', 'I') NOT NULL DEFAULT 'A',
  `idContaCredito` INT NOT NULL,
  `tipoContaCredito` ENUM('C', 'D') NOT NULL,
  `idContaDebito` INT NOT NULL,
  `tipoContaDebito` ENUM('C', 'D') NOT NULL,
  PRIMARY KEY (`idNotas`, `idContaCredito`, `tipoContaCredito`, `idContaDebito`, `tipoContaDebito`),
  CONSTRAINT `fk_tblNotas_tblContas`
    FOREIGN KEY (`idContaCredito` , `tipoContaCredito`)
    REFERENCES `dinheiro`.`tblContas` (`idConta` , `tipoConta`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_tblNotas_tblContas1`
    FOREIGN KEY (`idContaDebito` , `tipoContaDebito`)
    REFERENCES `dinheiro`.`tblContas` (`idConta` , `tipoConta`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE INDEX `fk_tblNotas_tblContas_idx` ON `dinheiro`.`tblNotas` (`idContaCredito` ASC, `tipoContaCredito` ASC) VISIBLE;

CREATE INDEX `fk_tblNotas_tblContas1_idx` ON `dinheiro`.`tblNotas` (`idContaDebito` ASC, `tipoContaDebito` ASC) VISIBLE;

CREATE INDEX `idxDatas` ON `dinheiro`.`tblNotas` (`dataNota` ASC, `valor` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `dinheiro`.`tblRazao`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `dinheiro`.`tblRazao` (
  `idConta` INT NOT NULL,
  `tipoConta` ENUM('C', 'D') NOT NULL,
  `periodoInicial` DATE NOT NULL,
  `periodoFinal` DATE NOT NULL,
  `SaldoAnterior` DECIMAL(9,2) NOT NULL,
  `Entradas` DECIMAL(9,2) NOT NULL,
  `Saidas` DECIMAL(9,2) NOT NULL,
  `SaldoFinal` DECIMAL(9,2) NOT NULL,
  `situacao` ENUM('A', 'F') NOT NULL DEFAULT 'A',
  `criado` DATE NOT NULL,
  `modificado` DATE NOT NULL,
  `status` ENUM('A', 'I') NOT NULL DEFAULT 'A',
  PRIMARY KEY (`idConta`, `tipoConta`, `periodoInicial`),
  CONSTRAINT `fk_tblRazao_tblContas1`
    FOREIGN KEY (`idConta` , `tipoConta`)
    REFERENCES `dinheiro`.`tblContas` (`idConta` , `tipoConta`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE INDEX `idxRazao` ON `dinheiro`.`tblRazao` (`tipoConta` ASC, `periodoInicial` ASC) VISIBLE;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
