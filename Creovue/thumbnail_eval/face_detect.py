#  Creovue/thumbnail_eval/face_detect.py
import os
import cv2
import numpy as np
from flask import Blueprint, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename

face_bp = Blueprint(
    'face_detection',
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/thumbnail'
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
#UPLOAD_FOLDER = '/tmp/creovue_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@face_bp.route('/face-detect', methods=['GET', 'POST'])
def face_detect():
    faces_count = 0
    image_url = None

    if request.method == 'POST':
        file = request.files.get('thumbnail')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(save_path)

            # Face detection
            image = cv2.imread(save_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
            faces_count = len(faces)

            for (x, y, w, h) in faces:
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

            result_filename = f"faces_{filename}"
            result_path = os.path.join(UPLOAD_FOLDER, result_filename)
            cv2.imwrite(result_path, image)

            # Image URL for template rendering
            image_url = url_for('face_detection.static', filename=f"uploads/{result_filename}")

        else:
            flash('Invalid file format. Please upload a JPG, JPEG, or PNG image.', 'danger')

    return render_template('face_detect.html', image_url=image_url, faces_count=faces_count)

