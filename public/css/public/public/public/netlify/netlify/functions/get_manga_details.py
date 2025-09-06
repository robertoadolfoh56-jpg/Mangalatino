import sqlite3
import json

def get_db_connection():
    conn = sqlite3.connect('mangas.db')
    conn.row_factory = sqlite3.Row
    return conn

def handler(event, context):
    try:
        manga_id = event['queryStringParameters'].get('id')
        if not manga_id:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Falta el ID del manga'})}

        conn = get_db_connection()
        manga = conn.execute('SELECT * FROM mangas WHERE id = ?', (manga_id,)).fetchone()
        if not manga:
            return {'statusCode': 404, 'body': json.dumps({'error': 'Manga no encontrado'})}

        chapters = conn.execute('SELECT * FROM chapters WHERE manga_id = ? ORDER BY id', (manga_id,)).fetchall()
        conn.close()

        response_data = {
            'details': dict(manga),
            'chapters': [dict(chapter) for chapter in chapters]
        }
        return {
            'statusCode': 200,
            'headers': { 'Content-Type': 'application/json' },
            'body': json.dumps(response_data)
        }
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
