from flask import Flask, render_template
import os
import db
import numpy as np
import pickle

app = Flask(__name__)

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