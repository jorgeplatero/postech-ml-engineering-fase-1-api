import logging
import joblib


logger = logging.getLogger(__name__)

try:
    model = joblib.load('data/ml_artifacts/model.pkl')
    logger.info('Modelo carregado com sucesso')
except FileNotFoundError:
    logger.error('Arquivo "model.pkl" não encontrado.')
    model = None