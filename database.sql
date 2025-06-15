CREATE DATABASE HealthMe;
USE HealthMe;

CREATE TABLE UsersAccount (
    UserID int PRIMARY KEY AUTO_INCREMENT,
    Email varchar(255),
    Pass varchar(255)
);

CREATE TABLE UsersProfiles (
    UserID int PRIMARY KEY,
    FirstName varchar(255),    
    LastName varchar(255),    
    Age int(11),    
    Height double,
    Weight double,
    Sex varchar(10),
    BMI float,
    FOREIGN KEY (UserID) REFERENCES UsersAccount(UserID) ON DELETE CASCADE
);