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

def get_faces(img_path, dir_path):
    #face detection and alignment
    face_objs = DeepFace.extract_faces(img_path=img_path, 
            target_size = (224, 224), 
            detector_backend = "retinaface"
    )
    image = cv2.imread(img_path)
    height, width, _ = image.shape
    results = {}
    for idx, face in enumerate(face_objs):

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
        face_path = os.path.join(dir_path, f'face_{idx}.jpg')
        cv2.imwrite(face_path, cropped_face)
        results[face_path] = {
            'coordinates': {
                'x1': x1,
                'y1': y1,
                'x2': x2,
                'y2': y2
            }
        }

    return results

def populate_db():
    for pick in tqdm(glob('dl/pickles/*.pickle')):
        for face in pickle(open(pick, 'rb').read()):
            data = {}
            data['folder_name'] = face['imagePath'].split('/')[-2]
            data['image_name'] = face['imagePath'].split('/')[-1]
            data['location'] = {
                'y1': face['loc'][0],
                'x2': face['loc'][1],
                'y2': face['loc'][2],
                'x1': face['loc'][3]
            }
            data['encoding'] = pickle.dumps(face['encoding'])
            data['tagged'] = False
            # db.insert_data('faces', temp_dict)

@app.route('/tag_results', methods=['POST'])
def tag_results():

    if request.method == 'POST':
        data = request.json
        image_path = data[0]['image_path']
        dir_name = os.path.join('static', 'temp_data', os.path.basename(image_path).split('.')[0])
        if os.path.exists(dir_name):
            info_path = os.path.join(dir_name, 'info.json')
            with open(info_path, 'r') as f:
                info = json.load(f)
        else:
            print("RAISE A 500 Error and redirect")
            return "Unsuccessful"
        
        for face in data[1:]:
            info['faces'][face['face_path']]['label'] = face['face_label']
        
        with open(info_path, 'w') as f:
            json.dump(info, f)
    else:
        print("RAISE A 500 Error and redirect")
        return "Unsuccessful"

    return "Successful!"


@app.route('/tag_faces', methods=['POST'])
def tag_faces():
    
    print(request.form["image_path"])
    path = request.form["image_path"]
    dir_name = os.path.join('static', 'temp_data', os.path.basename(path).split('.')[0])
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    detected_faces = get_faces(path, dir_name)

    labels = ['Praneet', 'Smriti', 'Sourav', 'Akshay']
    faces = list(detected_faces.keys())

    info = {
        'picture_path': path,
        'faces': detected_faces.copy()
    }
    info_path = os.path.join(dir_name, 'info.json')
    for i in range(len(faces)):
        info['faces'][faces[i]]['label'] = 'Unknown'

    with open(info_path, 'w') as f:
        json.dump(info, f)

    return render_template('tag_faces.html', path=path, faces=faces, labels=labels)

@app.route('/', methods=['GET', 'POST'])
def index():
    # temp = pickle.dumps(np.array([123, 1234, 456]))
    # temp_dict = {
    #     'data': temp
    # }
    # print(album_name)
    if request.method == 'GET':
        path = ''
    else:
        path = request.form.get("folder", "")
    # else:
    #     path = ''
    # db.insert_data('faces', temp_dict)
    folders, images = get_files(path)
    return render_template('index.html', folders=folders, images=images)





if __name__ == '__main__':
    app.run(debug=True)