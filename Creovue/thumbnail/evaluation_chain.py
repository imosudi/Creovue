# Creovue/thumbnail/evaluation_chain.py
import os
import cv2
import numpy as np
import pytesseract
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Blueprint, request, render_template, url_for, flash, current_app
from flask_security import login_required

from werkzeug.utils import secure_filename

from skimage import exposure

# Blueprint setup
eval_chain_bp = Blueprint('thumbnail_summary', __name__, template_folder='templates', url_prefix='/thumbnail')

UPLOAD_FOLDER = 'uploads'
HEATMAP_FOLDER = 'heatmaps'
TEXT_OVERLAY_FOLDER = 'text_overlay'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_folder(relative_path):
    folder = os.path.join(current_app.static_folder, relative_path)
    os.makedirs(folder, exist_ok=True)
    return folder

@eval_chain_bp.route('/summary', methods=['GET', 'POST'])
@login_required
def thumbnail_summary():
    image_url = face_result_url = heatmap_url = text_overlay_url = None
    text_count = 0
    text_recommendation = ""
    ctr_score = 0
    ctr_feedback = []

    if request.method == 'POST':
        file = request.files.get('thumbnail')

        if not (file and allowed_file(file.filename)):
            flash("Invalid image format. Upload PNG, JPG or JPEG.", 'danger')
            return render_template('summary.html')

        filename = secure_filename(file.filename)
        upload_folder = get_folder(UPLOAD_FOLDER)
        heatmap_folder = get_folder(HEATMAP_FOLDER)
        text_overlay_folder = get_folder(TEXT_OVERLAY_FOLDER)

        save_path = os.path.join(upload_folder, filename)
        file.save(save_path)

        image_url = url_for('static', filename=f'{UPLOAD_FOLDER}/{filename}')

        ##### FACE DETECTION #####
        image = cv2.imread(save_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        face_count = len(faces)

        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        face_result_filename = f"face_{filename}"
        face_result_path = os.path.join(upload_folder, face_result_filename)
        cv2.imwrite(face_result_path, image)
        face_result_url = url_for('static', filename=f'{UPLOAD_FOLDER}/{face_result_filename}')

        ##### COLOUR HEATMAP #####
        gray_img = cv2.cvtColor(cv2.imread(save_path), cv2.COLOR_BGR2GRAY)
        plt.figure(figsize=(6, 6))
        plt.imshow(gray_img, cmap='hot', interpolation='nearest')
        plt.axis('off')
        heatmap_filename = f"heatmap_{filename}"
        heatmap_path = os.path.join(heatmap_folder, heatmap_filename)
        plt.savefig(heatmap_path, bbox_inches='tight', pad_inches=0)
        plt.close()
        heatmap_url = url_for('static', filename=f'{HEATMAP_FOLDER}/{heatmap_filename}')

        ##### TEXT DENSITY #####
        image = cv2.imread(save_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        resized = cv2.resize(enhanced, None, fx=2, fy=2)
        thresh = cv2.adaptiveThreshold(resized, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 15, 9)
        custom_config = r'--oem 3 --psm 6'
        boxes = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT, config=custom_config)

        total_area = 0
        for i in range(len(boxes['text'])):
            text = boxes['text'][i].strip()
            conf = int(boxes['conf'][i])
            if text and conf >= 40:
                x, y, w, h = [int(v / 2) for v in (boxes['left'][i], boxes['top'][i], boxes['width'][i], boxes['height'][i])]
                text_count += 1
                total_area += w * h
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        image_area = image.shape[0] * image.shape[1]
        text_ratio = total_area / image_area if image_area > 0 else 0

        if text_count == 0:
            text_recommendation = "⚠️ No text detected. Use bold titles."
        elif text_count > 20:
            text_recommendation = "⚠️ Too much text. Simplify message."
        elif text_ratio > 0.3:
            text_recommendation = "⚠️ High text coverage. Reduce clutter."
        else:
            text_recommendation = "✅ Text density looks optimal."

        text_overlay_name = f"overlay_{filename}"
        overlay_path = os.path.join(text_overlay_folder, text_overlay_name)
        cv2.imwrite(overlay_path, image)
        text_overlay_url = url_for('static', filename=f'{TEXT_OVERLAY_FOLDER}/{text_overlay_name}')

        ##### CTR PREDICTION #####
        score = 0
        ctr_image = cv2.imread(save_path)
        gray = cv2.cvtColor(ctr_image, cv2.COLOR_BGR2GRAY)

        # Contrast
        if gray.std() > 50:
            score += 1.5
            ctr_feedback.append("✅ High contrast")
        else:
            ctr_feedback.append("⚠️ Low contrast")

        # Face size
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)
        if len(faces) > 0:
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
            if (w * h) / (gray.shape[0] * gray.shape[1]) > 0.1:
                score += 2.0
                ctr_feedback.append("✅ Prominent face")
            else:
                ctr_feedback.append("⚠️ Face too small")
        else:
            ctr_feedback.append("⚠️ No face")
        

        # Colour clutter
        hsv = cv2.cvtColor(ctr_image, cv2.COLOR_BGR2HSV)
        s = hsv[:, :, 1]
        if np.sum(s > 128) / s.size < 0.25:
            score += 1.0
            ctr_feedback.append("✅ Few strong colours")
        else:
            ctr_feedback.append("⚠️ Colour clutter")

        # Layout clarity
        blur = cv2.GaussianBlur(gray, (9, 9), 0)
        _, binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        if np.sum(binary == 255) / binary.size > 0.2:
            score += 1.0
            ctr_feedback.append("✅ Clean layout")
        else:
            ctr_feedback.append("⚠️ Layout clutter")

        # Text presence
        ocr = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        text_blocks = sum(1 for t in ocr['text'] if t.strip())
        if 1 <= text_blocks <= 10:
            score += 1.5
            ctr_feedback.append("✅ Text quantity appropriate")
        elif text_blocks == 0:
            ctr_feedback.append("⚠️ No text")
        else:
            ctr_feedback.append("⚠️ Too much text")

        ctr_score = min(round(score * 2, 1), 10.0)

    return render_template(
        'summary.html',
        image_url=image_url,
        face_result_url=face_result_url,
        heatmap_url=heatmap_url,
        text_overlay_url=text_overlay_url,
        text_count=text_count,
        text_recommendation=text_recommendation,
        ctr_score=ctr_score,
        ctr_feedback=ctr_feedback
    )
