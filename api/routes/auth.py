import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from api.extensions import db, bcrypt
from api.models.user import User
from api.models.user_access import UserAccess
from api.scripts.auth_utils import get_user_by_username


logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register_user():
    '''
    Registra um novo usuário.
    ---
    tags:
        - Auth
    parameters:
        - in: body
          name: body
          required: true
          description: Credenciais do usuário.
          schema:
            type: object
            properties:
                username:
                    type: string
                password:
                    type: string
    responses:
        201:
            description: Usuário criado com sucesso.
            schema:
                type: object
                properties:
                    msg:
                        type: string
                        description: Mensagem de successo para registro de usuário.
            examples:
                application/json:
                    msg: 'Usuário criado com sucesso'
        400:
            description: Usuário já existe.
            schema:
                type: object
                properties:
                    error:
                        type: string
                        description: Mensagem de erro para registro de usuário.
            examples:
                application/json:
                    error: 'Usuário já existe'
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
    data = request.get_json(force=True)
    if get_user_by_username(data['username']):
        return jsonify({'error': 'Usuário já existe'}), 400
    try:
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = User(username=data['username'], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f'error: {e}')
        return jsonify({'error': 'Erro interno ao registrar usuário'}), 500
    return jsonify({'msg': 'Usuário criado com sucesso'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    '''
    Gera um token JWT para autenticação.
    ---
    tags:
      - Auth
    parameters:
        - in: body
          name: body
          required: true
          description: Credenciais do usuário.
          schema:
              type: object
              properties:
                  username:
                      type: string
                  password:
                      type: string
    responses:
        200:
            description: Login bem sucedido, retorna o token JWT
            schema:
                type: object
                properties:
                    access_token:
                        type: string
                        description: O token de acesso JWT
            examples:
                application/json:
                    access_token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
        400:
            description: Usuário já existe.
            schema:
                type: object
                properties:
                    error:
                        type: string
                        description: Mensagem de erro de autenticação.
            examples:
                application/json:
                    error: 'Usuário e senha são obrigatórios'
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
    data = request.get_json(force=True)
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Usuário e senha são obrigatórios'}), 400
    user = get_user_by_username(username)
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({'error': 'Usuário ou senha inválidas'}), 401
    try:
        access = UserAccess(username=data['username'], created_at=datetime.utcnow())
        db.session.add(access)
        access_token = create_access_token(identity=str(user.id))
        return jsonify({'access_token': access_token}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f'error: {e}')
        return jsonify({'error': e}), 500