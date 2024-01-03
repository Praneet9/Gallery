import os

HOST = 'localhost'
PORT = 3306
USER = 'praneet'
DB = 'gallery'
PASSWORD = os.environ.get('MYSQL_PASSWORD')
GUNNERS_NAMES = ['Praneet', 'Smriti', 'Sourav', 'Akshay', 
				  'Denis', 'Amenda', 'Rinita', 'Alroy',
				  'Charles', 'Michael', 'Nikhil', 'Unknown']
# Percentages of the width and the height of the face
LEFT_PAD = 25 / 100
TOP_PAD = 20 / 100
RIGHT_PAD = 20 / 100
BOTTOM_PAD = 10 / 100
FACE_CONF = 90 / 100