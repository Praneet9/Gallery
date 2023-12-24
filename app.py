from flask import Flask, render_template, request
import os
import db
import numpy as np
import pickle
from glob import glob
import cv2
import json

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
        dir_name = os.path.join('static', 'data', os.path.basename(image_path).split('.')[0])
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

    return "Successful!"


@app.route('/tag_faces', methods=['POST'])
def tag_faces():
    
    path = 'static/data/B612_20170909_145018.jpg'
    dir_name = os.path.join('static', 'data', os.path.basename(path).split('.')[0])
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)

    labels = ['Praneet', 'Smriti', 'Sourav', 'Akshay']
    faces = [path.replace('B612_20170909_145018', i) for i in labels]

    info = {
        'picture_path': path,
        'faces': {}
    }
    info_path = os.path.join(dir_name, 'info.json')
    for i in range(len(faces)):
        info['faces'][faces[i]] = {
            'coordinates': [],
            'label': 'Unknown'
        }

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