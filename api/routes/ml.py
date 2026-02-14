import logging
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from scripts.ml_utils import get_prediction, get_user_predictions


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
    
    response, status_code = get_prediction(user_id, data)
    
    return jsonify(response), status_code


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
        400:
            description: Parâmetros de paginação inválidos.
            schema:
                type: object
                properties:
                    error:
                        type: string
                        description: Mensagem de erro de validação.
            examples:
                application/json:
                    error: 'Parâmetros limit ou offset inválidos'
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

    try:
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 0))
    except ValueError:
        return jsonify({'error': 'Parâmetros limit ou offset inválidos'}), 400
    
    results, error = get_user_predictions(user_id, limit, offset)
    
    if results is None:
        return jsonify({'error': error}), 500
        
    return jsonify(results)