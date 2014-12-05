CREATE DATABASE  IF NOT EXISTS `test_database` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `test_database`;
-- MySQL dump 10.13  Distrib 5.6.13, for Win32 (x86)
--
-- Host: localhost    Database: test_database
-- ------------------------------------------------------
-- Server version	5.6.17

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `employees`
--

DROP TABLE IF EXISTS `employees`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `employees` (
  `emp_no` int(4) NOT NULL,
  `first_name` varchar(50) DEFAULT NULL,
  `last_name` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`emp_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employees`
--

LOCK TABLES `employees` WRITE;
/*!40000 ALTER TABLE `employees` DISABLE KEYS */;
INSERT INTO `employees` VALUES (1,'Bill','Lannister'),(2,'George','Stark'),(3,'Ivor','Baelish'),(4,'Nicolas','Baratheon'),(5,'Robert','Clegane'),(6,'Paul','Tarly');
/*!40000 ALTER TABLE `employees` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `failures`
--

DROP TABLE IF EXISTS `failures`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `failures` (
  `fail_id` int(11) NOT NULL,
  `stat_code` varchar(45) DEFAULT NULL,
  `MTTF_hour` float DEFAULT NULL,
  PRIMARY KEY (`fail_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `failures`
--

LOCK TABLES `failures` WRITE;
/*!40000 ALTER TABLE `failures` DISABLE KEYS */;
INSERT INTO `failures` VALUES (1,'MILL1',1),(2,'MILL2',0.5),(3,'MILL1',0.5),(4,'MILL1',0.6),(5,'MILL1',0.8),(6,'MILL2',1),(7,'MILL2',0.6),(8,'MILL1',0.5),(9,'MILL2',0.3),(10,'MILL2',0.8),(11,'MILL1',0.9),(12,'MILL2',0.65),(13,'MILL2',0.35),(14,'MILL2',0.4),(15,'MILL1',0.2),(16,'MILL1',0.6),(17,'MILL1',0.65),(18,'MILL2',0.8),(19,'MILL1',0.9),(20,'MILL1',1),(21,'MILL2',0.4),(22,'MILL2',0.5),(23,'MILL2',0.65),(24,'MILL2',0.8),(25,'MILL2',0.9),(26,'MILL1',1),(27,'MILL1',0.45),(28,'MILL1',0.55),(29,'MILL1',0.4),(30,'MILL2',0.5),(31,'MILL1',1),(32,'MILL2',0.5),(33,'MILL1',0.5),(34,'MILL1',0.6),(35,'MILL1',0.8),(36,'MILL2',1),(37,'MILL2',0.6),(38,'MILL1',0.5),(39,'MILL2',0.3),(40,'MILL2',0.8),(41,'MILL1',0.9),(42,'MILL2',0.65),(43,'MILL2',0.35),(44,'MILL2',0.4),(45,'MILL1',0.2),(46,'MILL1',0.6),(47,'MILL1',0.65),(48,'MILL2',0.8),(49,'MILL1',0.9),(50,'MILL1',1),(51,'MILL2',0.4),(52,'MILL2',0.5),(53,'MILL2',0.65),(54,'MILL2',0.8),(55,'MILL2',0.9),(56,'MILL1',1),(57,'MILL1',0.45),(58,'MILL1',0.55),(59,'MILL1',0.4),(60,'MILL2',0.5),(61,'MILL1',1),(62,'MILL2',0.5),(63,'MILL1',0.5),(64,'MILL1',0.6),(65,'MILL1',0.8),(66,'MILL2',1),(67,'MILL2',0.6),(68,'MILL1',0.5),(69,'MILL2',0.3),(70,'MILL2',0.8),(71,'MILL1',0.9),(72,'MILL2',0.65),(73,'MILL2',0.35),(74,'MILL2',0.4),(75,'MILL1',0.2),(76,'MILL1',0.6),(77,'MILL1',0.65),(78,'MILL2',0.8),(79,'MILL1',0.9),(80,'MILL1',1);
/*!40000 ALTER TABLE `failures` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `production_status`
--

DROP TABLE IF EXISTS `production_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `production_status` (
  `prod_id` int(11) NOT NULL AUTO_INCREMENT,
  `prod_code` varchar(45) DEFAULT NULL,
  `stat_code` varchar(45) DEFAULT NULL,
  `emp_no` varchar(45) DEFAULT NULL,
  `TIMEIN` time DEFAULT NULL,
  `TIMEOUT` time DEFAULT NULL,
  PRIMARY KEY (`prod_id`)
) ENGINE=InnoDB AUTO_INCREMENT=71 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `production_status`
--

LOCK TABLES `production_status` WRITE;
/*!40000 ALTER TABLE `production_status` DISABLE KEYS */;
INSERT INTO `production_status` VALUES (1,'PE-0001','MILL1','2','08:49:29','08:50:50'),(2,'AP-0129','MILL2','3','08:47:24','08:48:14'),(3,'AP-0129','MILL1','2','08:51:10','08:52:04'),(4,'PE-0001','MILL2','3','08:49:09','08:50:00'),(5,'AP-0129','MILL2','3','08:50:23','08:51:32'),(6,'PE-0001','MILL1','2','08:52:39','08:53:01'),(7,'PE-0001','MILL2','3','08:51:50','08:52:40'),(8,'AP-0129','MILL1','2','08:53:16','08:54:01'),(9,'PE-0001','MILL2','1','08:52:59','08:53:48'),(10,'AP-0129','MILL1','4','08:54:14','08:55:09'),(11,'PE-0001','MILL2','1','08:54:01','08:54:45'),(12,'AP-0129','MILL2','1','08:55:00','08:55:45'),(13,'AP-0129','MILL1','4','08:55:15','08:56:05'),(14,'AP-0129','MILL2','1','08:55:45','08:56:30'),(15,'PE-0001','MILL1','4','08:56:10','08:57:05'),(16,'PE-0001','MILL2','1','08:56:45','08:57:15'),(17,'AP-0129','MILL1','4','08:57:05','08:58:05'),(18,'PE-0001','MILL1','4','08:58:15','08:59:15'),(19,'AP-0129','MILL2','1','08:57:30','08:58:20'),(20,'AP-0129','MILL1','4','08:59:15','09:00:10'),(21,'PE-0001','MILL2','1','08:58:40','08:59:30'),(22,'PE-0001','MILL1','4','09:00:19','09:01:00'),(23,'AP-0129','MILL2','1','08:59:45','09:00:30'),(24,'AP-0129','MILL2','1','09:00:50','09:01:40'),(25,'PE-0001','MILL1','5','09:01:00','09:01:45'),(26,'PE-0001','MILL2','6','09:01:40','09:02:30'),(27,'AP-0129','MILL1','5','09:01:45','09:02:30'),(28,'AP-0129','MILL2','6','09:02:30','09:03:25'),(29,'AP-0129','MILL2','6','09:03:25','09:04:10'),(30,'PE-0001','MILL1','5','09:02:30','09:03:25'),(31,'PE-0001','MILL1','5','09:03:35','09:04:15'),(32,'AP-0129','MILL2','6','09:04:20','09:05:10'),(33,'PE-0001','MILL2','6','09:05:10','09:06:20'),(34,'AP-0129','MILL1','5','09:04:15','09:05:10'),(35,'AP-0129','MILL1','5','09:05:10','09:06:05'),(36,'PE-0001','MILL1','2','08:49:29','08:50:50'),(37,'AP-0129','MILL2','3','08:47:24','08:48:14'),(38,'AP-0129','MILL1','2','08:51:10','08:52:04'),(39,'PE-0001','MILL2','3','08:49:09','08:50:00'),(40,'AP-0129','MILL2','3','08:50:23','08:51:32'),(41,'PE-0001','MILL1','2','08:52:39','08:53:01'),(42,'PE-0001','MILL2','3','08:51:50','08:52:40'),(43,'AP-0129','MILL1','2','08:53:16','08:54:01'),(44,'PE-0001','MILL2','1','08:52:59','08:53:48'),(45,'AP-0129','MILL1','4','08:54:14','08:55:09'),(46,'PE-0001','MILL2','1','08:54:01','08:54:45'),(47,'AP-0129','MILL2','1','08:55:00','08:55:45'),(48,'AP-0129','MILL1','4','08:55:15','08:56:05'),(49,'AP-0129','MILL2','1','08:55:45','08:56:30'),(50,'PE-0001','MILL1','4','08:56:10','08:57:05'),(51,'PE-0001','MILL2','1','08:56:45','08:57:15'),(52,'AP-0129','MILL1','4','08:57:05','08:58:05'),(53,'PE-0001','MILL1','4','08:58:15','08:59:15'),(54,'AP-0129','MILL2','1','08:57:30','08:58:20'),(55,'AP-0129','MILL1','4','08:59:15','09:00:10'),(56,'PE-0001','MILL2','1','08:58:40','08:59:30'),(57,'PE-0001','MILL1','4','09:00:19','09:01:00'),(58,'AP-0129','MILL2','1','08:59:45','09:00:30'),(59,'AP-0129','MILL2','1','09:00:50','09:01:40'),(60,'PE-0001','MILL1','5','09:01:00','09:01:45'),(61,'PE-0001','MILL2','6','09:01:40','09:02:30'),(62,'AP-0129','MILL1','5','09:01:45','09:02:30'),(63,'AP-0129','MILL2','6','09:02:30','09:03:25'),(64,'AP-0129','MILL2','6','09:03:25','09:04:10'),(65,'PE-0001','MILL1','5','09:02:30','09:03:25'),(66,'PE-0001','MILL1','5','09:03:35','09:04:15'),(67,'AP-0129','MILL2','6','09:04:20','09:05:10'),(68,'PE-0001','MILL2','6','09:05:10','09:06:20'),(69,'AP-0129','MILL1','5','09:04:15','09:05:10'),(70,'AP-0129','MILL1','5','09:05:10','09:06:05');
/*!40000 ALTER TABLE `production_status` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `products` (
  `prod_id` int(11) NOT NULL AUTO_INCREMENT,
  `prod_code` varchar(45) NOT NULL,
  `Name` varchar(75) DEFAULT NULL,
  PRIMARY KEY (`prod_id`,`prod_code`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES (1,'PE-0001','xxx'),(2,'AP-0129','yyy');
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `repairs`
--

DROP TABLE IF EXISTS `repairs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `repairs` (
  `rep_id` int(11) NOT NULL,
  `stat_code` varchar(45) DEFAULT NULL,
  `MTTR_hour` float DEFAULT NULL,
  PRIMARY KEY (`rep_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `repairs`
--

LOCK TABLES `repairs` WRITE;
/*!40000 ALTER TABLE `repairs` DISABLE KEYS */;
INSERT INTO `repairs` VALUES (1,'MILL1',0.1),(2,'MILL2',0.05),(3,'MILL1',0.2),(4,'MILL1',0.05),(5,'MILL1',0.02),(6,'MILL2',0.1),(7,'MILL2',0.15),(8,'MILL1',0.18),(9,'MILL2',0.1),(10,'MILL2',0.2),(11,'MILL1',0.05),(12,'MILL2',0.25),(13,'MILL2',0.15),(14,'MILL2',0.1),(15,'MILL1',0.05),(16,'MILL1',0.07),(17,'MILL1',0.08),(18,'MILL2',0.09),(19,'MILL1',0.1),(20,'MILL1',0.15),(21,'MILL2',0.16),(22,'MILL2',0.21),(23,'MILL2',0.18),(24,'MILL2',0.19),(25,'MILL2',0.11),(26,'MILL1',0.115),(27,'MILL1',0.17),(28,'MILL1',0.2),(29,'MILL1',0.1),(30,'MILL2',0.14),(31,'MILL1',0.1),(32,'MILL2',0.05),(33,'MILL1',0.2),(34,'MILL1',0.05),(35,'MILL1',0.02),(36,'MILL2',0.1),(37,'MILL2',0.15),(38,'MILL1',0.18),(39,'MILL2',0.1),(40,'MILL2',0.2),(41,'MILL1',0.05),(42,'MILL2',0.25),(43,'MILL2',0.15),(44,'MILL2',0.1),(45,'MILL1',0.05),(46,'MILL1',0.07),(47,'MILL1',0.08),(48,'MILL2',0.09),(49,'MILL1',0.1),(50,'MILL1',0.15),(51,'MILL2',0.16),(52,'MILL2',0.21),(53,'MILL2',0.18),(54,'MILL2',0.19),(55,'MILL2',0.11),(56,'MILL1',0.115),(57,'MILL1',0.17),(58,'MILL1',0.2),(59,'MILL1',0.1),(60,'MILL2',0.14),(61,'MILL1',0.1),(62,'MILL2',0.05),(63,'MILL1',0.2),(64,'MILL1',0.05),(65,'MILL1',0.02),(66,'MILL2',0.1),(67,'MILL2',0.15),(68,'MILL1',0.18),(69,'MILL2',0.1),(70,'MILL2',0.2),(71,'MILL1',0.05),(72,'MILL2',0.25),(73,'MILL2',0.15),(74,'MILL2',0.1),(75,'MILL1',0.05),(76,'MILL1',0.07),(77,'MILL1',0.08),(78,'MILL2',0.09),(79,'MILL1',0.1),(80,'MILL1',0.15);
/*!40000 ALTER TABLE `repairs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stations`
--

DROP TABLE IF EXISTS `stations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stations` (
  `stat_id` int(11) NOT NULL AUTO_INCREMENT,
  `stat_code` varchar(55) DEFAULT NULL,
  `stationName` varchar(75) DEFAULT NULL,
  PRIMARY KEY (`stat_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stations`
--

LOCK TABLES `stations` WRITE;
/*!40000 ALTER TABLE `stations` DISABLE KEYS */;
INSERT INTO `stations` VALUES (1,'MILL1','Milling Machine1'),(2,'MILL2','Milling Machine2');
/*!40000 ALTER TABLE `stations` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2014-06-16 12:01:14
