import os
from datetime import timedelta

class Config:
    SECRET_KEY = 'hard-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    JWT_SECRET_KEY = 'even-harder-jwt-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
