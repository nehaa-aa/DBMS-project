CREATE DATABASE IF NOT EXISTS smart_nutrition_bmi CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE smart_nutrition_bmi;

CREATE TABLE Users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  age INT,
  gender ENUM('Male','Female','Other') DEFAULT 'Other',
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE Biometrics (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  height_cm DECIMAL(5,2) NOT NULL,
  weight_kg DECIMAL(5,2) NOT NULL,
  bmi DECIMAL(4,1),
  goal ENUM('loss','gain','maintain') DEFAULT 'maintain',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_bio_user FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Food_Items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(150) NOT NULL UNIQUE,
  calories_per_100g DECIMAL(7,2) NOT NULL,
  protein_g DECIMAL(6,2) DEFAULT 0,
  carbs_g DECIMAL(6,2) DEFAULT 0,
  fat_g DECIMAL(6,2) DEFAULT 0
) ENGINE=InnoDB;

CREATE TABLE Meal_Logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  food_id INT NOT NULL,
  eaten_at DATETIME NOT NULL,
  quantity_g DECIMAL(8,2) NOT NULL,
  calories DECIMAL(10,2),
  CONSTRAINT fk_meal_user FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
  CONSTRAINT fk_meal_food FOREIGN KEY (food_id) REFERENCES Food_Items(id) ON DELETE RESTRICT,
  INDEX idx_meal_user_date (user_id, eaten_at)
) ENGINE=InnoDB;
