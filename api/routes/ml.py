import logging
import numpy as np
from flask import Blueprint, jsonify, request
from api.models.predictions import Predictions
from api.extensions import db
from . import model
from flask_jwt_extended import jwt_required, get_jwt_identity


logger = logging.getLogger(__name__)
ml_bp = Blueprint('ml', __name__, url_prefix='/api/v1/ml')


@ml_bp.route('/predict', methods=['POST'])
@jwt_required()
def predict():
    '''
    Realiza uma predição com o modelo Iris e armazena o resultado.
    ---
    tags:
        - ML
    security:
        - BearerAuth: []
    parameters:
        - in: body
          name: body
          required: true
          description: Parâmetros de entrada do modelo.
          schema:
              type: object
              properties:
                  sepal_length:
                      type: number
                      format: float
                      description: Comprimento da sépala (cm).
                      example: 5.1
                  sepal_width:
                      type: number
                      format: float
                      description: Largura da sépala (cm).
                      example: 3.5
                  petal_length:
                      type: number
                      format: float
                      description: Comprimento da pétala (cm).
                      example: 1.4
                  petal_width:
                      type: number
                      format: float
                      description: Largura da pétala (cm).
                      example: 0.2
    responses:
        200:
            description: Predição realizada.
            schema:
                type: object
                properties:
                    predicted_specie:
                        type: string
                        description: Classe prevista.
            examples:
                application/json:
                    predicted_specie: 'setosa'
        401:
            description: Erro de autenticação JWT.
            schema:
                type: object
                properties:
                    error:
                        type: string
                        description: Mensagem de erro de autenticação.
            examples:
                application/json:
                    error: '<erro de autenticação>'
        500:
            description: Erro interno do servidor.
            schema:
                type: object
                properties:
                    error:
                        type: string
                        description: Mensagem de erro interno do servidor.
            examples:
                application/json:
                    error: '<erro interno do servidor>'
    '''
    user_id = get_jwt_identity()
    
    data = request.get_json(force=True)
    try:
        sepal_length = float(data['sepal_length'])
        sepal_width = float(data['sepal_width'])
        petal_length = float(data['petal_length'])
        petal_width = float(data['petal_width'])
    except (ValueError, KeyError) as e:
        logger.error('Dados de entrada inválidos')
        return jsonify({'error': 'Dados inválidos, verifique parâmetros'}), 400

    features = [sepal_length, sepal_width, petal_length, petal_width]
    input_data = np.array([features])
    
    try:
        prediction = model.predict(input_data)
        predicted_class = int(prediction[0])
        predicted_specie_name = {
            0: 'setosa',
            1: 'versicolor',
            2: 'virginica'
        }.get(predicted_class)
    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': 'Erro ao gerar predição'}), 500
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
        logger.error(f'error: {e}')
    return jsonify({'predicted_specie': predicted_specie_name})


@ml_bp.route('/predictions', methods=['GET'])
@jwt_required()
def predictions():
    '''
    Lista as predições armazenadas no banco, com paginação.
    ---
    tags:
        - ML
    security:
        - BearerAuth: []
    parameters:
        - in: query
          name: limit
          type: integer
          required: false
          default: 10
          description: Número máximo de registros para retornar.
        - in: query
          name: offset
          type: integer
          required: false
          default: 0
          description: Número de registros a ignorar (para paginação).
    responses:
        200:
            description: Lista de predições do usuário.
            schema:
                type: array
                items:
                    type: object
                    properties:
                        id:
                            type: integer
                        sepal_length:
                            type: number
                        sepal_width:
                            type: number
                        petal_length:
                            type: number
                        petal_width:
                            type: number
                        predicted_class:
                            type: integer
                        predicted_specie:
                            type: string
                        created_at:
                            type: string
                            format: datetime
            examples:
                application/json:
                    id: 1
                    petal_length: 38.95
                    petal_width: 1.4
                    predicted_class: 1.0
                    predicted_specie: 0
                    sepal_length: 1.1
                    sepal_width: 10.5
                    created_at: '2026-02-01T19:21:17.370208'
        401:
            description: Erro de autenticação JWT.
            schema:
                type: object
                properties:
                    error:
                        type: string
                        description: Mensagem de erro de autenticação.
            examples:
                application/json:
                    error: '<erro de autenticação>'
        500:
            description: Erro interno do servidor.
            schema:
                type: object
                properties:
                    error:
                        type: string
                        description: Mensagem de erro interno do servidor.
            examples:
                application/json:
                    error: '<erro interno do servidor>'
    '''
    user_id = get_jwt_identity()
    
    limit = int(request.args.get('limit', 10))
    offset = int(request.args.get('offset', 0))
    
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

    return jsonify(results)