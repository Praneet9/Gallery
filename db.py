import mysql.connector as connector
from mysql.connector import Error


def get_connection(host, port, password, database):

    try:
        connection = connector.connect(
            host=host, port=port, 
            passwd=password, database=database
        )
    except Error as err:
        connection = None
        print(f"MySQL connection failed due to: {err}")

    return connection


def read_query(connection, query, conditions=()):
    cursor = connection.cursor()
    try:
        cursor.execute(query, conditions)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Query failed due to: {err}")
        return None


def insert_face_tags(connection, info):

    query = "INSERT INTO gunners (x1, x2, y1, y2, file_path, face_id, name, confidence) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
    
    file_path = info.get('picture_path')
    records = [
        (face['coordinates']['x1'], face['coordinates']['x2'],
         face['coordinates']['y1'], face['coordinates']['y2'],
         file_path, face['face_id'], face['label'], round(face['confidence'], 3))
         for face in info['faces'].values()
    ]
    
    cursor = connection.cursor()
    try:
        cursor.executemany(query, records)
        connection.commit()
        return True
    except Error as err:
        print(f"Query failed due to: {err}")
        return False


def update_face_tags(connection, info):

    query = "UPDATE gunners SET face_id = %s, name = %s, tagged = %s \
            WHERE file_path = %s AND face_id = %s;"
    
    cursor = connection.cursor()
    try:
        cursor.executemany(query, info)
        connection.commit()
        return True
    except Error as err:
        print(f"Query failed due to: {err}")
        return False


def remove_face(connection, img_path, face_id):

    query = "DELETE FROM gunners WHERE file_path = %s AND face_id = %s;"
    cursor = connection.cursor()
    try:
        cursor.execute(query, (img_path, face_id))
        connection.commit()
        return True
    except Error as err:
        print(f"Query failed due to: {err}")
        return False


def get_dir_info(connection, dir_path):
    query = "SELECT DISTINCT(file_path), tagged FROM gunners WHERE file_path LIKE %s;"
    conditions = (dir_path + '%', )
    cursor = connection.cursor()
    try:
        cursor.execute(query, conditions)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Query failed due to: {err}")
        return []