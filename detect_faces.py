from glob import glob
from deepface import DeepFace
import cv2
import os
import config as cfg
import mysql.connector as connector
from mysql.connector import Error
import db
from tqdm import tqdm


def insert_face_tags(connection, info):

    query = "INSERT INTO gunners (x1, x2, y1, y2, file_path, face_id, name, confidence, tagged) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
    
    file_path = info.get('picture_path')
    records = [
        (face['coordinates']['x1'], face['coordinates']['x2'],
         face['coordinates']['y1'], face['coordinates']['y2'],
         file_path, face['face_id'], face['label'],
         round(face['confidence'], 3), False)
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

def get_faces(img_path):
     
	face_objs = DeepFace.extract_faces(img_path=img_path, 
            target_size = (224, 224), 
            detector_backend = "retinaface"
    )
	image = cv2.imread(img_path)
	height, width, _ = image.shape
	results = {}
	for face_id, face in enumerate(face_objs):

		if face['confidence'] < cfg.FACE_CONF:
			continue

		w = face['facial_area']['w']
		h = face['facial_area']['h']

		x1 = face['facial_area']['x'] - (w * cfg.LEFT_PAD)
		x2 = face['facial_area']['x'] + w + (w * cfg.RIGHT_PAD)
		y1 = face['facial_area']['y'] - (h * cfg.TOP_PAD)
		y2 = face['facial_area']['y'] + h + (h * cfg.BOTTOM_PAD)

		x1 = int(max(0, x1))
		x2 = int(min(x2, width))
		y1 = int(max(0, y1))
		y2 = int(min(y2, height))

		face_path = f'face_{face_id}.jpg'
		results[face_path] = {
			'coordinates': {
				'x1': x1,
				'y1': y1,
				'x2': x2,
				'y2': y2
			},
			'confidence': face['confidence'], 
			'face_id': face_id,
			'label': "Unknown"
		}
	info = {
		'picture_path': img_path,
		'faces': results.copy(),
	}

	return info

images = glob('static/data/Andrews_College/*/*.jpg')
images += glob('static/data/Andrews_College/*/*.png')
images += glob('static/data/Andrews_College/*/*.jpeg')
conn = db.get_connection(cfg.HOST, cfg.PORT, cfg.PASSWORD, cfg.DB)
failed_counter = 1

for image_path in tqdm(images):
    
	try:
		info = get_faces(image_path)
		success = insert_face_tags(conn, info)
	except Exception as e:
		print(f"{failed_counter}) Had a problem with {image_path} || Error: {e}")
		failed_counter += 1

conn.close()