import os
class Config:
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'smart_nutrition_bmi')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
