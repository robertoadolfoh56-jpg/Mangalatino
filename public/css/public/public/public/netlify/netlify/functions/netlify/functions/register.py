import sqlite3
import json
from werkzeug.security import generate_password_hash

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
        if not username or not password:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Faltan datos'})}

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user:
            conn.close()
            return {'statusCode': 409, 'body': json.dumps({'error': 'El nombre de usuario ya existe'})}
        
        password_hash = generate_password_hash(password)
        conn.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
        conn.commit()
        conn.close()
        return {'statusCode': 201, 'body': json.dumps({'message': 'Usuario creado con éxito'})}
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
