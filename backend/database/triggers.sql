USE smart_nutrition_bmi;
DELIMITER //
CREATE TRIGGER trg_biometrics_bmi_bi BEFORE INSERT ON Biometrics
FOR EACH ROW
BEGIN
  IF NEW.height_cm > 0 THEN
    SET NEW.bmi = ROUND(NEW.weight_kg / POWER(NEW.height_cm/100, 2), 1);
  END IF;
END//
CREATE TRIGGER trg_biometrics_bmi_bu BEFORE UPDATE ON Biometrics
FOR EACH ROW
BEGIN
  IF NEW.height_cm > 0 THEN
    SET NEW.bmi = ROUND(NEW.weight_kg / POWER(NEW.height_cm/100, 2), 1);
  END IF;
END//
CREATE TRIGGER trg_meal_cal_bi BEFORE INSERT ON Meal_Logs
FOR EACH ROW
BEGIN
  DECLARE cal100 DECIMAL(7,2);
  SELECT calories_per_100g INTO cal100 FROM Food_Items WHERE id = NEW.food_id;
  IF cal100 IS NOT NULL THEN
    SET NEW.calories = ROUND((cal100/100.0) * NEW.quantity_g, 2);
  END IF;
END//
DELIMITER ;
