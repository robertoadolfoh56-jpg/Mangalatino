import sqlite3
import json
import os

ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

def get_db_connection():
    conn = sqlite3.connect('mangas.db')
    return conn

def handler(event, context):
    if event['httpMethod'] != 'POST':
        return {'statusCode': 405, 'body': json.dumps({'error': 'Método no permitido'})}
        
    try:
        data = json.loads(event['body'])
        password = data.get('password')
        manga_id = data.get('manga_id')

        if password != ADMIN_PASSWORD:
            return {'statusCode': 403, 'body': json.dumps({'error': 'Contraseña incorrecta'})}

        conn = get_db_connection()
        # Borramos en orden para no violar las restricciones de la base de datos
        conn.execute('DELETE FROM pages WHERE chapter_id IN (SELECT id FROM chapters WHERE manga_id = ?)', (manga_id,))
        conn.execute('DELETE FROM chapters WHERE manga_id = ?', (manga_id,))
        conn.execute('DELETE FROM mangas WHERE id = ?', (manga_id,))
        conn.commit()
        conn.close()

        return {'statusCode': 200, 'body': json.dumps({'message': 'Manga eliminado de la base de datos'})}
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
