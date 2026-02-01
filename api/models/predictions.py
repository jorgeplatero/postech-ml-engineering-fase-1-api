import logging
from datetime import datetime
from api.extensions import db


logger = logging.getLogger(__name__)


class Predictions(db.Model):
    '''Modelo de dados para armazenar o histórico de predições do modelo Iris.'''
    __tablename__ = 'predictions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    sepal_length = db.Column(db.Float, nullable=False)
    sepal_width = db.Column(db.Float, nullable=False)
    petal_length = db.Column(db.Float, nullable=False)
    petal_width = db.Column(db.Float, nullable=False)
    predicted_class = db.Column(db.Integer, nullable=False)
    predicted_specie = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Prediction {self.id} -> {self.predicted_specie}>'