from flask import Flask, render_template, request
import os
import db
import numpy as np
import pickle
from glob import glob
import cv2
import json
from deepface import DeepFace
import config as cfg

app = Flask(__name__)
HOME_DIR = '/home/praneet/Projects/Gallery/'
ABSOLUTE_PATH = '/home/praneet/Projects/Gallery/static/data/'

def get_files(path):

    dir_path = os.path.abspath(os.path.join(ABSOLUTE_PATH, path))
    if not dir_path.startswith(ABSOLUTE_PATH):
        dir_path = os.path.join(ABSOLUTE_PATH)

    data_list = os.listdir(dir_path)
    data_list = [os.path.join(dir_path, i) for i in data_list]
    folders = [i.replace(ABSOLUTE_PATH, "") for i in data_list if os.path.isdir(i)]
    images = [i.replace(HOME_DIR, "") for i in data_list if i.endswith(('.png', '.jpg', '.jpeg'))]
    if folders:
        folders = [os.path.join(os.path.dirname(folders[0]), '..')] + folders
    return folders, images

def extract_faces(img_path, dir_path):
    #face detection and alignment
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

        cropped_face = image[y1:y2, x1:x2]
        face_path = os.path.join(dir_path, f'face_{face_id}.jpg')
        cv2.imwrite(face_path, cropped_face)
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

    return results

def get_faces(face_objs, img_path, dir_path):

    image = cv2.imread(img_path)
    results = {}
    for face in face_objs:
        
        x1, x2, y1, y2 = face[1:5]
        face_id, name, confidence = face[6:]

        if confidence < cfg.FACE_CONF:
            continue

        cropped_face = image[y1:y2, x1:x2]
        face_path = os.path.join(dir_path, f'face_{face_id}.jpg')
        cv2.imwrite(face_path, cropped_face)
        results[face_path] = {
            'coordinates': {
                'x1': x1,
                'y1': y1,
                'x2': x2,
                'y2': y2
            },
            'confidence': confidence, 
            'face_id': face_id,
            'label': name
        }

    return results


@app.route('/remove_face', methods=['POST'])
def remove_face():
    if request.method == 'POST':
        data = request.json
        image_path = data[0]['image_path']
        face_id = int(data[0]['face_id'])

        conn = db.get_connection(cfg.HOST, cfg.PORT, cfg.PASSWORD, cfg.DB)
        success = db.remove_face(conn, image_path, face_id)
        conn.close()

        if success:
            return "Delete Successful"
        else:
            return "Unsuccessful"


@app.route('/tag_results', methods=['POST'])
def tag_results():

    if request.method == 'POST':
        data = request.json
        image_path = data[0]['image_path']
        
        info = [(face['face_id'], face['face_label'], image_path, face['face_id']) for face in data[1:]]

        conn = db.get_connection(cfg.HOST, cfg.PORT, cfg.PASSWORD, cfg.DB)
        success = db.update_face_tags(conn, info)
        conn.close()

        if not success:
            print("FAILED TO ADD TO DB! SHOW DIALOG")
        
    else:
        print("RAISE A 500 Error and redirect")
        return "Unsuccessful"

    return "Successful!"


@app.route('/tag_faces', methods=['POST'])
def tag_faces():
    
    path = request.form["image_path"]
    dir_name = os.path.join('static', 'temp_data', os.path.basename(path).split('.')[0])
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    query = "SELECT * FROM gunners WHERE file_path = %s;"
    records = (path, )
    conn = db.get_connection(cfg.HOST, cfg.PORT, cfg.PASSWORD, cfg.DB)
    detected_faces = db.read_query(conn, query, records)
    conn.close()
    
    if detected_faces:
        detected_faces = get_faces(detected_faces, path, dir_name)
    else:
        detected_faces = extract_faces(path, dir_name)
        info = {
            'picture_path': path,
            'faces': detected_faces.copy()
        }
        conn = db.get_connection(cfg.HOST, cfg.PORT, cfg.PASSWORD, cfg.DB)
        success = db.insert_face_tags(conn, info)
        conn.close()

        if not success:
            print("FAILED TO ADD TO DB! SHOW DIALOG")

    return render_template('tag_faces.html', path=path, detected_faces=detected_faces, labels=cfg.GUNNERS_NAMES)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        path = ''
    else:
        path = request.form.get("folder", "")
    folders, images = get_files(path)
    return render_template('index.html', folders=folders, images=images)





if __name__ == '__main__':
    app.run(debug=True)