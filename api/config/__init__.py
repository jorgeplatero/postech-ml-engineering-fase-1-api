import logging
import os
from dotenv import load_dotenv
from datetime import timedelta


logger = logging.getLogger(__name__)
load_dotenv(override=True)


class Config(object):
    '''Configuração da API para Predição de Espécies Iris'''
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///predictions.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'MEUSEGREDOAQUI')
    JWT_ALGORITHM = 'HS256'
    SWAGGER = {
        'title': 'Predição de Espécies Iris',
        'uiversion': 3,
        'description': 'API para predição de espécies Iris.'
    }
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=1440)

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True