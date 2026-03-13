import os
from flask import Config
from sqlalchemy import create_engine

class Config(object):
    SECRET_KEY ="Clave secreta"
    SESSION_COOKIE_SECURE=False
    
class DevelopmentConfig(Config):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:Lucero2117@127.0.0.1/examenPizzas'
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    