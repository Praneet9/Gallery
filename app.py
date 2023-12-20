from flask import Flask, render_template, request
import os
import db
import numpy as np
import pickle
from glob import glob
import cv2
import shutil as su
import json

app = Flask(__name__)
DATA_PATH = '/home/praneet/Projects/Face_Recognition/Dataset'

def get_files(path):

    data_list = glob(os.path.join(DATA_PATH, path, '*'))
    folders = [os.path.basename(i) for i in data_list if os.path.isdir(i)]
    images = [i for i in data_list if i.endswith(('.png', '.jpg', '.jpeg'))]
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
    
    # print(request.form)
    # path=(request.form.get('image_path'))
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

@app.route('/<string:dir_name>')
def list_images(dir_name):
    folders, images = get_files(os.path.join(DATA_PATH, dir_name))
    return render_template('image_grid.html', folders=folders, images=images)

@app.route('/')
def index():
    # temp = pickle.dumps(np.array([123, 1234, 456]))
    # temp_dict = {
    #     'data': temp
    # }
    # print(album_name)
    # if request.method == 'GET':
    # else:
    #     path = ''
    # db.insert_data('faces', temp_dict)
    folders, images = get_files()
    
    return render_template('index.html', folders=folders, images=images)





if __name__ == '__main__':
    app.run(debug=True)