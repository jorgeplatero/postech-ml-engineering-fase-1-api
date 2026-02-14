import logging
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from api.models.predictions import Predictions
from api.extensions import db
from . import model


logger = logging.getLogger('__name__')


def get_prediction(
        user_id: int, 
        data: Dict[str, Any]
    ) -> Tuple[Dict[str, str], int]:
    '''
    Realiza uma predição com o modelo Iris, valida os dados de entrada e armazena no banco.

    Args:
        user_id (int): O ID do usuário autenticado que está realizando a predição.
        data (dict): Dicionário contendo as chaves 'sepal_length', 'sepal_width', 
                    'petal_length' e 'petal_width'.

    Returns:
        tuple: Um dicionário com o resultado ou erro e um inteiro com o status HTTP.
            Ex: ({'predicted_specie': 'setosa'}, 200)
    '''
    try:
        sepal_length = float(data['sepal_length'])
        sepal_width = float(data['sepal_width'])
        petal_length = float(data['petal_length'])
        petal_width = float(data['petal_width'])
    except (ValueError, KeyError, TypeError):
        return {'error': 'Dados inválidos, verifique parâmetros'}, 400

    try:
        features = [sepal_length, sepal_width, petal_length, petal_width]
        input_data = np.array([features])
        prediction = model.predict(input_data)
        predicted_class = int(prediction[0])
        
        species_map = {0: 'setosa', 1: 'versicolor', 2: 'virginica'}
        predicted_specie_name = species_map.get(predicted_class, 'unknown')
    except Exception as e:
        logger.error(f'Erro na predição: {e}')
        return {'error': 'Erro interno ao gerar predição'}, 500

    try:
        new_pred = Predictions(
            user_id=user_id,
            sepal_length=sepal_length,
            sepal_width=sepal_width,
            petal_length=petal_length,
            petal_width=petal_width,
            predicted_class=predicted_class,
            predicted_specie=predicted_specie_name,
        )
        db.session.add(new_pred)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f'Erro ao salvar no banco: {e}')

    return {'predicted_specie': predicted_specie_name}, 200


def get_user_predictions(
        user_id: int, 
        limit: int = 10, 
        offset: int = 0
    ) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    '''
    Busca as predições de um usuário específico no banco de dados com paginação.

    Args:
        user_id (int): O ID do usuário cujas predições serão buscadas.
        limit (int, optional): Número máximo de registros a retornar. Padrão é 10.
        offset (int, optional): Número de registros a pular. Padrão é 0.

    Returns:
        tuple: (lista_de_resultados, mensagem_de_erro)
    '''
    try:
        preds = Predictions.query.filter_by(user_id=user_id)\
            .order_by(Predictions.id.desc())\
            .limit(limit)\
            .offset(offset)\
            .all()
        
        results = []
        for p in preds:
            results.append({
                'id': p.id,
                'sepal_length': p.sepal_length,
                'sepal_width': p.sepal_width,
                'petal_length': p.petal_length,
                'petal_width': p.petal_width,
                'predicted_class': p.predicted_class,
                'predicted_specie': p.predicted_specie,
                'created_at': p.created_at.isoformat()
            })
        
        return results, None
    except Exception as e:
        logger.error(f'Erro ao listar predições: {e}')
        return None, str(e)