from flask import Flask, render_template
import os
import db
import numpy as np
import pickle
from glob import glob

app = Flask(__name__)

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
            db.insert_data('faces', temp_dict)

@app.route('/')
def index():
    temp = pickle.dumps(np.array([123, 1234, 456]))
    temp_dict = {
        'data': temp
    }
    
    db.insert_data('faces', temp_dict)
    folders = os.listdir('/home/praneet/Downloads/Compressed/images_data/Andrews College/')
    return render_template('index.html', folders = folders)





if __name__ == '__main__':
    app.run(debug=True)