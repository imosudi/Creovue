# Creovue/thumbnail/ctr_predict.py
import os
import cv2
import numpy as np
from flask import Blueprint, request, render_template, url_for, flash, current_app
from flask_security import login_required

from werkzeug.utils import secure_filename
from skimage import exposure
from flask import jsonify
import pytesseract

ctr_bp = Blueprint(
    'ctr_predict',
    __name__,
    template_folder='templates',
    url_prefix='/thumbnail'
)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Ensure upload folder exists
def get_folder(relative_path):
    folder = os.path.join(current_app.static_folder, relative_path)
    os.makedirs(folder, exist_ok=True)
    return folder

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@ctr_bp.route('/ctr-score', methods=['GET', 'POST'])
@login_required
def ctr_score():
    image_url = None
    score = 0
    feedback = []

    if request.method == 'POST':
        file = request.files.get('thumbnail')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_folder = get_folder(UPLOAD_FOLDER)
            save_path = os.path.join(upload_folder, filename)
            file.save(save_path)

            image = cv2.imread(save_path)
            if image is None:
                flash("Invalid image format.", 'danger')
                return render_template('ctr_score.html')

            image_url = url_for('static', filename=f'{UPLOAD_FOLDER}/{filename}')

            # Heuristic 1: High contrast check
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            contrast = gray.std()
            if contrast > 50:
                score += 1.5
                feedback.append("✅ High contrast")
            else:
                feedback.append("⚠️ Low contrast")

            # Heuristic 2: Large human face present?
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
            if len(faces) > 0:
                x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
                face_area = w * h / (image.shape[0] * image.shape[1])
                if face_area > 0.1:
                    score += 2.0
                    feedback.append("✅ Prominent human face")
                else:
                    feedback.append("⚠️ Face detected but too small")
            else:
                feedback.append("⚠️ No face detected")

            # Heuristic 3: Few strong colours (low clutter)
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            _, s, v = cv2.split(hsv)
            saturated_pixels = np.sum(s > 128)
            if saturated_pixels / s.size < 0.25:
                score += 1.0
                feedback.append("✅ Limited strong colours")
            else:
                feedback.append("⚠️ Too many vivid colours")

            # Heuristic 4: Clean layout (white space)
            blur = cv2.GaussianBlur(gray, (9, 9), 0)
            _, binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            white_space_ratio = np.sum(binary == 255) / binary.size
            if white_space_ratio > 0.2:
                score += 1.0
                feedback.append("✅ Clean layout with breathing space")
            else:
                feedback.append("⚠️ Layout may be cluttered")

            # Heuristic 5: Text not overcrowded (use OCR count threshold)
            import pytesseract
            ocr_text = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
            text_count = sum(1 for t in ocr_text['text'] if t.strip())
            if 1 <= text_count <= 10:
                score += 1.5
                feedback.append("✅ Text quantity is appropriate")
            elif text_count == 0:
                feedback.append("⚠️ No text detected")
            else:
                feedback.append("⚠️ Too much text")

            # Final scale to 10
            score = min(round(score * 2, 1), 10.0)

        else:
            flash("Unsupported file type.", 'danger')

    return render_template('ctr_score.html', image_url=image_url, score=score, feedback=feedback)



@ctr_bp.route('/api/ctr-score', methods=['POST'])
@login_required
def ctr_score_api():
    file = request.files.get('thumbnail')
    if not file or not allowed_file(file.filename):
        return jsonify({"error": "Unsupported or missing image"}), 400

    filename = secure_filename(file.filename)
    upload_folder = get_folder(UPLOAD_FOLDER)
    save_path = os.path.join(upload_folder, filename)
    file.save(save_path)

    image = cv2.imread(save_path)
    if image is None:
        return jsonify({"error": "Failed to read image"}), 400

    score = 0
    feedback = []

    # Heuristic 1: High contrast check
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    contrast = gray.std()
    if contrast > 50:
        score += 1.5
        feedback.append("✅ High contrast")
    else:
        feedback.append("⚠️ Low contrast")

    # Heuristic 2: Large human face
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    if len(faces) > 0:
        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
        face_area = w * h / (image.shape[0] * image.shape[1])
        if face_area > 0.1:
            score += 2.0
            feedback.append("✅ Prominent human face")
        else:
            feedback.append("⚠️ Face detected but too small")
    else:
        feedback.append("⚠️ No face detected")

    # Heuristic 3: Few strong colours
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    _, s, v = cv2.split(hsv)
    saturated_pixels = np.sum(s > 128)
    if saturated_pixels / s.size < 0.25:
        score += 1.0
        feedback.append("✅ Limited strong colours")
    else:
        feedback.append("⚠️ Too many vivid colours")

    # Heuristic 4: Clean layout
    blur = cv2.GaussianBlur(gray, (9, 9), 0)
    _, binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    white_space_ratio = np.sum(binary == 255) / binary.size
    if white_space_ratio > 0.2:
        score += 1.0
        feedback.append("✅ Clean layout with breathing space")
    else:
        feedback.append("⚠️ Layout may be cluttered")

    # Heuristic 5: Text detection via OCR
    ocr_text = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
    text_count = sum(1 for t in ocr_text['text'] if t.strip())
    if 1 <= text_count <= 10:
        score += 1.5
        feedback.append("✅ Text quantity is appropriate")
    elif text_count == 0:
        feedback.append("⚠️ No text detected")
    else:
        feedback.append("⚠️ Too much text")

    # Final score
    final_score = min(round(score * 2, 1), 10.0)

    return jsonify({
        "ctr_score": final_score,
        "feedback": feedback,
        "image_url": url_for('static', filename=f'{UPLOAD_FOLDER}/{filename}', _external=True)
    })
