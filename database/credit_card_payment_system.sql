-- MySQL dump 10.13  Distrib 8.0.46, for Linux (x86_64)
--
-- Host: localhost    Database: credit_card_payment_system
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `accounts_card`
--

DROP TABLE IF EXISTS `accounts_card`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts_card` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `card_type` varchar(10) NOT NULL,
  `masked_card_number` varchar(19) NOT NULL,
  `last_four_digits` varchar(4) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `accounts_card_user_id_8c234847_fk_accounts_user_id` (`user_id`),
  CONSTRAINT `accounts_card_user_id_8c234847_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_card`
--

LOCK TABLES `accounts_card` WRITE;
/*!40000 ALTER TABLE `accounts_card` DISABLE KEYS */;
INSERT INTO `accounts_card` VALUES (1,'credit','**** **** **** 1111','1111','2026-10-05 15:51:02.016841',1),(2,'credit','**** **** **** 4242','4242','2026-10-06 08:14:22.417061',1);
/*!40000 ALTER TABLE `accounts_card` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_user`
--

DROP TABLE IF EXISTS `accounts_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts_user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `email` varchar(254) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_user`
--

LOCK TABLES `accounts_user` WRITE;
/*!40000 ALTER TABLE `accounts_user` DISABLE KEYS */;
INSERT INTO `accounts_user` VALUES (1,'pbkdf2_sha256$1000000$BFdzQL0Z81d5hBTCKnk3Ee$w24rAQ3+sXaEHuEUALAfxsC8CL8hWrsW5+vU0taFLag=','2026-10-05 16:04:25.984136',1,'arun','','',1,1,'2026-10-05 15:48:29.069203','aaru2892@gmail.com'),(2,'pbkdf2_sha256$1000000$NacB6ntKV3Gaw46IO2MLkq$AlfEkkPt9LZFJ1v1TjAj8mMPwI8LB6XLe30QcHjiano=',NULL,0,'testuser','','',0,1,'2026-10-05 18:20:54.320314','test@user.com');
/*!40000 ALTER TABLE `accounts_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_user_groups`
--

DROP TABLE IF EXISTS `accounts_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accounts_user_groups_user_id_group_id_59c0b32f_uniq` (`user_id`,`group_id`),
  KEY `accounts_user_groups_group_id_bd11a704_fk_auth_group_id` (`group_id`),
  CONSTRAINT `accounts_user_groups_group_id_bd11a704_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `accounts_user_groups_user_id_52b62117_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_user_groups`
--

LOCK TABLES `accounts_user_groups` WRITE;
/*!40000 ALTER TABLE `accounts_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `accounts_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_user_user_permissions`
--

DROP TABLE IF EXISTS `accounts_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accounts_user_user_permi_user_id_permission_id_2ab516c2_uniq` (`user_id`,`permission_id`),
  KEY `accounts_user_user_p_permission_id_113bb443_fk_auth_perm` (`permission_id`),
  CONSTRAINT `accounts_user_user_p_permission_id_113bb443_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `accounts_user_user_p_user_id_e4f0a161_fk_accounts_` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_user_user_permissions`
--

LOCK TABLES `accounts_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `accounts_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `accounts_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add Blacklisted Token',6,'add_blacklistedtoken'),(22,'Can change Blacklisted Token',6,'change_blacklistedtoken'),(23,'Can delete Blacklisted Token',6,'delete_blacklistedtoken'),(24,'Can view Blacklisted Token',6,'view_blacklistedtoken'),(25,'Can add Outstanding Token',7,'add_outstandingtoken'),(26,'Can change Outstanding Token',7,'change_outstandingtoken'),(27,'Can delete Outstanding Token',7,'delete_outstandingtoken'),(28,'Can view Outstanding Token',7,'view_outstandingtoken'),(29,'Can add user',8,'add_user'),(30,'Can change user',8,'change_user'),(31,'Can delete user',8,'delete_user'),(32,'Can view user',8,'view_user'),(33,'Can add card',9,'add_card'),(34,'Can change card',9,'change_card'),(35,'Can delete card',9,'delete_card'),(36,'Can view card',9,'view_card'),(37,'Can add transaction',10,'add_transaction'),(38,'Can change transaction',10,'change_transaction'),(39,'Can delete transaction',10,'delete_transaction'),(40,'Can view transaction',10,'view_transaction');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_accounts_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES (1,'2026-10-05 15:51:02.026772','1','credit - **** 1111',1,'[{\"added\": {}}]',9,1),(2,'2026-10-05 15:56:17.766141','1','Transaction #1 - SUCCESS',1,'[{\"added\": {}}]',10,1);
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (9,'accounts','card'),(8,'accounts','user'),(1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'contenttypes','contenttype'),(5,'sessions','session'),(6,'token_blacklist','blacklistedtoken'),(7,'token_blacklist','outstandingtoken'),(10,'transactions','transaction');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2026-10-05 15:36:12.748084'),(2,'contenttypes','0002_remove_content_type_name','2026-10-05 15:36:13.235911'),(3,'auth','0001_initial','2026-10-05 15:36:13.872518'),(4,'auth','0002_alter_permission_name_max_length','2026-10-05 15:36:14.033445'),(5,'auth','0003_alter_user_email_max_length','2026-10-05 15:36:14.046235'),(6,'auth','0004_alter_user_username_opts','2026-10-05 15:36:14.104970'),(7,'auth','0005_alter_user_last_login_null','2026-10-05 15:36:14.133971'),(8,'auth','0006_require_contenttypes_0002','2026-10-05 15:36:14.163419'),(9,'auth','0007_alter_validators_add_error_messages','2026-10-05 15:36:14.193608'),(10,'auth','0008_alter_user_username_max_length','2026-10-05 15:36:14.222265'),(11,'auth','0009_alter_user_last_name_max_length','2026-10-05 15:36:14.247569'),(12,'auth','0010_alter_group_name_max_length','2026-10-05 15:36:14.294083'),(13,'auth','0011_update_proxy_permissions','2026-10-05 15:36:14.315549'),(14,'auth','0012_alter_user_first_name_max_length','2026-10-05 15:36:14.331790'),(15,'accounts','0001_initial','2026-10-05 15:36:15.013191'),(16,'accounts','0002_card','2026-10-05 15:36:15.184113'),(17,'admin','0001_initial','2026-10-05 15:36:15.481311'),(18,'admin','0002_logentry_remove_auto_add','2026-10-05 15:36:15.508130'),(19,'admin','0003_logentry_add_action_flag_choices','2026-10-05 15:36:15.542303'),(20,'sessions','0001_initial','2026-10-05 15:36:15.651326'),(21,'token_blacklist','0001_initial','2026-10-05 15:36:16.034985'),(22,'token_blacklist','0002_outstandingtoken_jti_hex','2026-10-05 15:36:16.176083'),(23,'token_blacklist','0003_auto_20171017_2007','2026-10-05 15:36:16.229421'),(24,'token_blacklist','0004_auto_20171017_2013','2026-10-05 15:36:16.735612'),(25,'token_blacklist','0005_remove_outstandingtoken_jti','2026-10-05 15:36:17.079457'),(26,'token_blacklist','0006_auto_20171017_2113','2026-10-05 15:36:17.170709'),(27,'token_blacklist','0007_auto_20171017_2214','2026-10-05 15:36:17.627701'),(28,'token_blacklist','0008_migrate_to_bigautofield','2026-10-05 15:36:18.146625'),(29,'token_blacklist','0010_fix_migrate_to_bigautofield','2026-10-05 15:36:18.178530'),(30,'token_blacklist','0011_linearizes_history','2026-10-05 15:36:18.185008'),(31,'token_blacklist','0012_alter_outstandingtoken_user','2026-10-05 15:36:18.238812'),(32,'token_blacklist','0013_alter_blacklistedtoken_options_and_more','2026-10-05 15:36:18.281004'),(33,'transactions','0001_initial','2026-10-05 15:36:18.653518'),(34,'transactions','0002_transaction_failure_reason','2026-10-05 15:36:18.808714');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('9t2nvxohyz9bx85c7ydwbg7861cwcqhh','.eJxVjDsOwjAQBe_iGlnxVwslPWewdr1eHECOFCcV4u4kUgpo38y8t0q4LjWtvcxpZHVRRp1-N8L8LG0H_MB2n3Se2jKPpHdFH7Tr28TldT3cv4OKvW61QxfIOMZoo3hgN2BgYeNtJMoCDsAKy2Bos6zLBNmcLXtPAgShqM8X7Iw4UA:1xDlAw:BXGa_6M0PwsTa_dMXRbsJohf1ETeKSsDIk8oen2F318','2026-10-19 16:04:26.026267');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `token_blacklist_blacklistedtoken`
--

DROP TABLE IF EXISTS `token_blacklist_blacklistedtoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `token_blacklist_blacklistedtoken` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `blacklisted_at` datetime(6) NOT NULL,
  `token_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token_id` (`token_id`),
  CONSTRAINT `token_blacklist_blacklistedtoken_token_id_3cc7fe56_fk` FOREIGN KEY (`token_id`) REFERENCES `token_blacklist_outstandingtoken` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `token_blacklist_blacklistedtoken`
--

LOCK TABLES `token_blacklist_blacklistedtoken` WRITE;
/*!40000 ALTER TABLE `token_blacklist_blacklistedtoken` DISABLE KEYS */;
INSERT INTO `token_blacklist_blacklistedtoken` VALUES (1,'2026-10-05 16:04:54.322782',2),(2,'2026-10-05 18:22:11.296937',5),(3,'2026-10-05 18:24:19.794973',6),(4,'2026-10-06 08:31:23.806030',15),(5,'2026-10-06 09:13:49.114822',17),(6,'2026-10-06 09:42:04.092928',21);
/*!40000 ALTER TABLE `token_blacklist_blacklistedtoken` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `token_blacklist_outstandingtoken`
--

DROP TABLE IF EXISTS `token_blacklist_outstandingtoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `token_blacklist_outstandingtoken` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `token` longtext NOT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `expires_at` datetime(6) NOT NULL,
  `user_id` bigint DEFAULT NULL,
  `jti` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token_blacklist_outstandingtoken_jti_hex_d9bdf6f7_uniq` (`jti`),
  KEY `token_blacklist_outs_user_id_83bc629a_fk_accounts_` (`user_id`),
  CONSTRAINT `token_blacklist_outs_user_id_83bc629a_fk_accounts_` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `token_blacklist_outstandingtoken`
--

LOCK TABLES `token_blacklist_outstandingtoken` WRITE;
/*!40000 ALTER TABLE `token_blacklist_outstandingtoken` DISABLE KEYS */;
INSERT INTO `token_blacklist_outstandingtoken` VALUES (1,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTMwMTg5MCwiaWF0IjoxNzkxMjE1NDkwLCJqdGkiOiJjYTM2YTM3MDNlNjQ0ZjA3YjYwMTg4NWVmYWUyM2E5MCIsInVzZXJfaWQiOiIxIn0.QuSV8a36iwQ2Bi72fB0vT543X5S2HSjYtQLU-m2SCWs','2026-10-05 15:51:30.844451','2026-10-06 15:51:30.000000',1,'ca36a3703e644f07b601885efae23a90'),(2,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTMwMjY3OSwiaWF0IjoxNzkxMjE2Mjc5LCJqdGkiOiI4OWFiMjBjMDc5YTc0NTBjODRhOWRkOWE3MmMwMDQzYiIsInVzZXJfaWQiOiIxIn0.BEKpvFRsMDCV3L7bq448nf54dQgryy_vlV7uN0SHT-8','2026-10-05 16:04:39.537560','2026-10-06 16:04:39.000000',1,'89ab20c079a7450c84a9dd9a72c0043b'),(3,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTMwMjcwMywiaWF0IjoxNzkxMjE2MzAzLCJqdGkiOiI1ODE1NjZiYzY3NDQ0OTcyODliNDY4OGUzYjIxZDQxYiIsInVzZXJfaWQiOiIxIn0.cDM4D7G78xQJW8ePgIqshV8IZvpm1qG6L0M7sGWusGg','2026-10-05 16:05:03.026617','2026-10-06 16:05:03.000000',1,'581566bc6744497289b4688e3b21d41b'),(4,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTMwMjg2NywiaWF0IjoxNzkxMjE2NDY3LCJqdGkiOiI0YWU2YzEzMDE4YTY0OWM0ODU2Y2Q2ODAwMTE4ODAzYSIsInVzZXJfaWQiOiIxIn0.ke7PNpbNU9sfHyj7PUykkjvxBbZjZJHi96NhJUTR6rY','2026-10-05 16:07:47.374604','2026-10-06 16:07:47.000000',1,'4ae6c13018a649c4856cd6800118803a'),(5,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTMxMDg2OSwiaWF0IjoxNzkxMjI0NDY5LCJqdGkiOiIwYTQwYTUyYTM2MTY0MDAwODAxNzQ0ZmU2N2NhZDA5MCIsInVzZXJfaWQiOiIyIn0.vhSAmbdxtEwfP-T0U9S5HC_tBCJu3NvmwJkzrBEB7JY','2026-10-05 18:21:09.815456','2026-10-06 18:21:09.000000',2,'0a40a52a36164000801744fe67cad090'),(6,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTMxMDk0MywiaWF0IjoxNzkxMjI0NTQzLCJqdGkiOiJkODM3YWQwM2MwNDI0YjY3YTM3N2VhOTg1N2VmY2M0YiIsInVzZXJfaWQiOiIxIn0.Pkf6UQqR0i_TcVeHsE8bvFg24tk3bnvwiczpFd27lSI','2026-10-05 18:22:23.650317','2026-10-06 18:22:23.000000',1,'d837ad03c0424b67a377ea9857efcc4b'),(7,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTM0NjkxNiwiaWF0IjoxNzkxMjYwNTE2LCJqdGkiOiI3MGQ1ZDg4MzY2ODQ0MzFkOWI5ODk1MjU5NDUwYmIzMyIsInVzZXJfaWQiOiIxIn0.eHI98LYSBV-8VcXwpotT-hIt8sdBOmHXIB7vaZqdeKI','2026-10-06 04:21:56.519102','2026-10-07 04:21:56.000000',1,'70d5d8836684431d9b9895259450bb33'),(8,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTM1MTE5OCwiaWF0IjoxNzkxMjY0Nzk4LCJqdGkiOiIxMjc3OGE5NDgyNGY0YjlmODgwOTZjYmYxMGRlNGRhNSIsInVzZXJfaWQiOiIxIn0.o_Yky3LFNt4IEzlwrEwnaKuC1Xj1SlknYuwinmLIMrE','2026-10-06 05:33:18.618235','2026-10-07 05:33:18.000000',1,'12778a94824f4b9f88096cbf10de4da5'),(9,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTM1MTgwNywiaWF0IjoxNzkxMjY1NDA3LCJqdGkiOiI1NWZhMzhkODZjNzA0NjgzYTZlMjZiNzM5YmQ0NzY4MyIsInVzZXJfaWQiOiIxIn0.j4TDcdGZaUsWWKtEh0WO51zRWXpWZ6wDtbwymwk9P5U','2026-10-06 05:43:27.350063','2026-10-07 05:43:27.000000',1,'55fa38d86c704683a6e26b739bd47683'),(10,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTM1NDIzMiwiaWF0IjoxNzkxMjY3ODMyLCJqdGkiOiIwMGQwZWY1NWJmNTc0NjgzODA2Yzk3OTdiMjVhNjg0NyIsInVzZXJfaWQiOiIxIn0.o_7vk-S3FcEryar8qHuNMw5CkYmqAt2MA0QVJmZKcQI','2026-10-06 06:23:52.468826','2026-10-07 06:23:52.000000',1,'00d0ef55bf574683806c9797b25a6847'),(11,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTM2MDU5MSwiaWF0IjoxNzkxMjc0MTkxLCJqdGkiOiJjMWI1OTUzMzc1NzQ0ZjZiYjMyMmQ4NzljMGNlZWZiMSIsInVzZXJfaWQiOiIxIn0.9HJEx015O097WaIkzA0SWpw7QPVCeUTj-lxPs4SV4e8','2026-10-06 08:09:51.900062','2026-10-07 08:09:51.000000',1,'c1b5953375744f6bb322d879c0ceefb1'),(12,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTM2MDk1NSwiaWF0IjoxNzkxMjc0NTU1LCJqdGkiOiJmNDI0Nzk0MzUwMWY0ZGFjOTU3OTI5MWE3ZTU3OTFjYiIsInVzZXJfaWQiOiIxIn0.dGOvGvm75UbscqvjBRodcOLwVkppizPtxidSbnOMt4k','2026-10-06 08:15:55.393139','2026-10-07 08:15:55.000000',1,'f4247943501f4dac9579291a7e5791cb'),(13,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTM2MTI5MywiaWF0IjoxNzkxMjc0ODkzLCJqdGkiOiI1ZmEwNWYxNWUwYzk0ZmUxYWY4N2IwNWEzODdlN2JmYyIsInVzZXJfaWQiOiIxIn0.8qdX4N3ZXsAh0URQezjIjhIZ9ZiDBVh0eyTSfRoyAsk','2026-10-06 08:21:33.355515','2026-10-07 08:21:33.000000',1,'5fa05f15e0c94fe1af87b05a387e7bfc'),(14,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTM2MTM2OCwiaWF0IjoxNzkxMjc0OTY4LCJqdGkiOiJkZjA1ODJlNzkxOTA0YmViYTVkNmU5YTBkOWI3Y2ZkMCIsInVzZXJfaWQiOiIxIn0.Ex1Ek_40F5vRwnHofLhOz4l5BaUJhoIBbHbvILB4Ips','2026-10-06 08:22:48.456104','2026-10-07 08:22:48.000000',1,'df0582e791904beba5d6e9a0d9b7cfd0'),(15,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTM2MTY1NCwiaWF0IjoxNzkxMjc1MjU0LCJqdGkiOiJiNmU1ZDVlNjBhMjQ0NTBjYjc1ZTFmNDQxOWQyYjMwMCIsInVzZXJfaWQiOiIxIn0.nQ0qiqMJveXMl8dLTL9xD_wZ4EgXj8q1NkEGmczG_qs','2026-10-06 08:27:34.022008','2026-10-07 08:27:34.000000',1,'b6e5d5e60a24450cb75e1f4419d2b300'),(16,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTM2MzgyNSwiaWF0IjoxNzkxMjc3NDI1LCJqdGkiOiJlNDZiZjFjZTY0ZTA0MThhOTY1MTFjY2IwYWQ2N2FjYSIsInVzZXJfaWQiOiIxIn0.oG_wS5HaG7wrEoMBHjNObM5tzfTrRoJdZqOXiqh6alY','2026-10-06 09:03:45.582800','2026-10-07 09:03:45.000000',1,'e46bf1ce64e0418a96511ccb0ad67aca'),(17,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTM2NDE1OCwiaWF0IjoxNzkxMjc3NzU4LCJqdGkiOiI4ODUxZWMzMTI0MjM0YmEzOWE1NDZhNzY2YjI3NzA2MyIsInVzZXJfaWQiOiIxIn0.7JJhXpq3ItktMbYbclZ-wLk4_BK0Agz68ibhHbtFrd4','2026-10-06 09:09:18.852629','2026-10-07 09:09:18.000000',1,'8851ec3124234ba39a546a766b277063'),(18,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTM2NDQzNiwiaWF0IjoxNzkxMjc4MDM2LCJqdGkiOiJjMjNkNDMyNjViNmQ0MjAxYjFlNTBiYjNkNDczNDQxMCIsInVzZXJfaWQiOiIxIn0.y42hwVOhqhoZDCloopjpruBGMt4sCu3pKABHSgGOhNQ','2026-10-06 09:13:56.725753','2026-10-07 09:13:56.000000',1,'c23d43265b6d4201b1e50bb3d4734410'),(19,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTM2NTM2MCwiaWF0IjoxNzkxMjc4OTYwLCJqdGkiOiIxNWQ4NTcwZDFjMDQ0Mjk1YjBkNDQ2OTE1MWVkNDJmNSIsInVzZXJfaWQiOiIxIn0.ktpUiNMaOhHvf5DFwwEWMtMdckEaubjyE9UKfM_CZE4','2026-10-06 09:29:20.285578','2026-10-07 09:29:20.000000',1,'15d8570d1c044295b0d4469151ed42f5'),(20,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTM2NTY4MCwiaWF0IjoxNzkxMjc5MjgwLCJqdGkiOiI3MmYzYzdkNjhjNTA0NjYzODQ4MjEwOGM1MzM0MWJiOCIsInVzZXJfaWQiOiIxIn0.ooo4YQSR8lZiqjkq6nAzFiMURwY8UYoLCkeZtt9HCwY','2026-10-06 09:34:40.735010','2026-10-07 09:34:40.000000',1,'72f3c7d68c5046638482108c53341bb8'),(21,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTM2NjA3MSwiaWF0IjoxNzkxMjc5NjcxLCJqdGkiOiIyMzhhNzUzNDZkNmE0MTM1OGM3ZWZiYjMwOTUzMzI2MCIsInVzZXJfaWQiOiIxIn0.ErweP2AODqfolsih1xM9QDbBh8hiarFbQg3JVwP4KA8','2026-10-06 09:41:11.272073','2026-10-07 09:41:11.000000',1,'238a75346d6a41358c7efbb309533260'),(22,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTM2NjE0OCwiaWF0IjoxNzkxMjc5NzQ4LCJqdGkiOiJiMzA3NDYyNWY5MTg0MGE0OTNhMDEzN2NkMDdmNzIyYiIsInVzZXJfaWQiOiIxIn0.6r3a8IEDkEUS0yWxI1n9uRyJDUeBKiEyEQoGbU-YiTs','2026-10-06 09:42:28.923610','2026-10-07 09:42:28.000000',1,'b3074625f91840a493a0137cd07f722b'),(23,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTM2Njk5NywiaWF0IjoxNzkxMjgwNTk3LCJqdGkiOiJkMGZjYzJhNTdkMjU0ZTNiYTI4N2U1NGQ1YzY1ZDlhYiIsInVzZXJfaWQiOiIxIn0.SlpnOjXIrVxDO5AhpD-wKMS3MT-Z0h0HCiAovTne3vA','2026-10-06 09:56:37.260764','2026-10-07 09:56:37.000000',1,'d0fcc2a57d254e3ba287e54d5c65d9ab'),(24,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTM2NzYyMywiaWF0IjoxNzkxMjgxMjIzLCJqdGkiOiI0YmFmZTViMWU4MWI0NDVhODgxMjRmYzA2MmRlODc4YyIsInVzZXJfaWQiOiIxIn0.BzgOFmqAvKYV7PIEsTZXLwLXBYflP0aNeQw67gNMjuk','2026-10-06 10:07:03.542689','2026-10-07 10:07:03.000000',1,'4bafe5b1e81b445a88124fc062de878c'),(25,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTM2ODEzMCwiaWF0IjoxNzkxMjgxNzMwLCJqdGkiOiI2NThjYjhlN2Y1ODc0MjRkOGMxOTJjNzI3YzMwNzY3MiIsInVzZXJfaWQiOiIxIn0.CWJnayl6RCyW4Z4e7pNWb2jvym6RCnfko7lc4DrnsKw','2026-10-06 10:15:30.812060','2026-10-07 10:15:30.000000',1,'658cb8e7f587424d8c192c727c307672');
/*!40000 ALTER TABLE `token_blacklist_outstandingtoken` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transactions_transaction`
--

DROP TABLE IF EXISTS `transactions_transaction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transactions_transaction` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `amount` decimal(10,2) NOT NULL,
  `status` varchar(10) NOT NULL,
  `transaction_date` datetime(6) NOT NULL,
  `card_id` bigint DEFAULT NULL,
  `user_id` bigint NOT NULL,
  `failure_reason` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `transactions_transaction_card_id_b6891695_fk_accounts_card_id` (`card_id`),
  KEY `transactions_transaction_user_id_b9ecc248_fk_accounts_user_id` (`user_id`),
  CONSTRAINT `transactions_transaction_card_id_b6891695_fk_accounts_card_id` FOREIGN KEY (`card_id`) REFERENCES `accounts_card` (`id`),
  CONSTRAINT `transactions_transaction_user_id_b9ecc248_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transactions_transaction`
--

LOCK TABLES `transactions_transaction` WRITE;
/*!40000 ALTER TABLE `transactions_transaction` DISABLE KEYS */;
INSERT INTO `transactions_transaction` VALUES (1,5000.00,'SUCCESS','2026-10-05 15:56:17.753561',1,1,NULL),(2,2999.00,'SUCCESS','2026-10-05 16:05:16.557770',1,1,NULL),(3,100001.00,'FAILED','2026-10-05 16:05:53.381100',1,1,'Payment declined because the amount exceeds the simulated gateway limit of ₹100,000'),(4,499.00,'SUCCESS','2026-10-05 18:22:43.690281',1,1,NULL),(5,285.00,'SUCCESS','2026-10-05 18:23:02.324514',1,1,NULL),(6,5000.00,'SUCCESS','2026-10-06 08:16:17.293475',2,1,NULL),(7,100001.00,'FAILED','2026-10-06 08:17:36.375953',2,1,'Payment declined because the amount exceeds the simulated gateway limit of ₹100,000'),(8,100001.00,'FAILED','2026-10-06 08:21:43.788278',2,1,'Payment declined because the amount exceeds the simulated gateway limit of ₹100,000');
/*!40000 ALTER TABLE `transactions_transaction` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-06 11:14:15
