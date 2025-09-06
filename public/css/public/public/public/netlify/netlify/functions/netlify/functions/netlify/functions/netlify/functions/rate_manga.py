import sqlite3
import json
import os
import jwt

SECRET_KEY = os.environ.get('SECRET_KEY', 'clave-por-defecto')

def get_db_connection():
    conn = sqlite3.connect('mangas.db')
    conn.row_factory = sqlite3.Row
    return conn

def handler(event, context):
    if event['httpMethod'] != 'POST':
        return {'statusCode': 405, 'body': json.dumps({'error': 'Método no permitido'})}

    try:
        # 1. Validar el token JWT del header
        auth_header = event['headers'].get('authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {'statusCode': 401, 'body': json.dumps({'error': 'Falta el token de autorización'})}
        
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return {'statusCode': 401, 'body': json.dumps({'error': 'Token inválido o expirado'})}

    # 2. Procesar la calificación
    try:
        data = json.loads(event['body'])
        score = int(data.get('score'))
        manga_id = int(event['queryStringParameters'].get('id')) # Se pasará como ?id=X

        conn = get_db_connection()
        # Insertar o actualizar el voto
        conn.execute('INSERT INTO ratings (user_id, manga_id, score) VALUES (?, ?, ?) ON CONFLICT(user_id, manga_id) DO UPDATE SET score = excluded.score', (user_id, manga_id, score))
        
        # Recalcular el promedio
        avg_data = conn.execute('SELECT AVG(score), COUNT(score) FROM ratings WHERE manga_id = ?', (manga_id,)).fetchone()
        new_avg, new_count = (avg_data[0] or 0.0, avg_data[1] or 0)
        conn.execute('UPDATE mangas SET avg_rating = ?, rating_count = ? WHERE id = ?', (new_avg, new_count, manga_id))
        
        conn.commit()
        conn.close()

        return {'statusCode': 200, 'body': json.dumps({'success': True, 'new_avg_rating': new_avg, 'new_rating_count': new_count})}
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
