-- Create the parking management database
CREATE DATABASE IF NOT EXISTS parking_db;
USE parking_db;

-- Create the vehicles table
CREATE TABLE IF NOT EXISTS vehicles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    number INT UNIQUE NOT NULL,
    license_plate VARCHAR(50) NOT NULL UNIQUE,
    vehicle_type VARCHAR(50) NOT NULL,
    time_of_entry DATETIME NOT NULL,
    time_of_exit DATETIME,
    duration INT,
    vehicle_image LONGBLOB,
    image_filename VARCHAR(255),
    status ENUM('parked', 'exited') DEFAULT 'parked',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create index for faster queries
CREATE INDEX idx_license_plate ON vehicles(license_plate);
CREATE INDEX idx_status ON vehicles(status);
CREATE INDEX idx_time_of_entry ON vehicles(time_of_entry);
