

import os
import cv2
import numpy as np
from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, current_app

from werkzeug.utils import secure_filename

face_bp = Blueprint(
    'face_detection',
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/thumbnail'
)

# Define base directory at module level
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RELATIVE_UPLOAD = 'static/uploads'

# Create a function to get the upload folder path
def get_upload_folder():
    if current_app:
        return os.path.join(current_app.root_path, RELATIVE_UPLOAD)
    else:
        # Fallback path for development/testing
        return os.path.join(BASE_DIR, 'static', 'uploads')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@face_bp.route('/face-detect', methods=['GET', 'POST'])
def face_detect():
    faces_count = 0
    image_url = None
    
    # Create upload folder if it doesn't exist
    UPLOAD_FOLDER = get_upload_folder()
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    if request.method == 'POST':
        file = request.files.get('thumbnail')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(save_path)

            # Face detection
            image = cv2.imread(save_path)
            
            if image is None or image.size == 0:
                # Handle the error appropriately, maybe return an error response
                return jsonify({"error": "Invalid or empty image provided"}), 400

            # Only proceed if we have a valid image
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
            image_url = url_for('thumbnail_eval/static', filename=f"uploads/{result_filename}")

        else:
            flash('Invalid file format. Please upload a JPG, JPEG, or PNG image.', 'danger')

    return render_template('face_detect.html', image_url=image_url, faces_count=faces_count)

# This ensures the upload folder exists when the blueprint is registered
@face_bp.record
def setup_blueprint(setup_state):
    app = setup_state.app
    with app.app_context():
        upload_folder = get_upload_folder()
        try:
            os.makedirs(upload_folder, exist_ok=True)    
        except :
            pass
        
        