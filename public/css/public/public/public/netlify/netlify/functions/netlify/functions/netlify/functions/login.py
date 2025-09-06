import sqlite3
import json
import os
import jwt
import time
from werkzeug.security import check_password_hash

SECRET_KEY = os.environ.get('SECRET_KEY', 'clave-por-defecto')

def get_db_connection():
    conn = sqlite3.connect('mangas.db')
    conn.row_factory = sqlite3.Row
    return conn

def handler(event, context):
    if event['httpMethod'] != 'POST':
        return {'statusCode': 405, 'body': json.dumps({'error': 'Método no permitido'})}
    try:
        data = json.loads(event['body'])
        username = data.get('username')
        password = data.get('password')
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if not user or not check_password_hash(user['password_hash'], password):
            return {'statusCode': 401, 'body': json.dumps({'error': 'Credenciales incorrectas'})}

        payload = {
            'user_id': user['id'],
            'username': user['username'],
            'exp': int(time.time()) + (60 * 60 * 24) # 24 horas de expiración
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Inicio de sesión exitoso', 'token': token})
        }
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
