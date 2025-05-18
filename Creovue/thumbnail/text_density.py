# Creovue/thumbnail/text_density.py
import os
import cv2
import pytesseract
from flask import Blueprint, request, render_template, flash, url_for, current_app
from werkzeug.utils import secure_filename

text_bp = Blueprint(
    'text_density',
    __name__,
    template_folder='templates',
    url_prefix='/thumbnail'
)

RELATIVE_UPLOAD = 'uploads'
RELATIVE_OUTPUT = 'text_overlay'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_folder(relative_path):
    folder = os.path.join(current_app.static_folder, relative_path)
    os.makedirs(folder, exist_ok=True)
    return folder

@text_bp.route('/text-density', methods=['GET', 'POST'])
def text_density():
    image_url = overlay_url = recommendation = None
    text_count = 0
    total_text_area = 0

    if request.method == 'POST':
        file = request.files.get('thumbnail')
        if not (file and allowed_file(file.filename)):
            flash('Invalid image format. Only PNG, JPG, JPEG supported.', 'danger')
            return render_template('text_density.html')

        # Paths
        filename = secure_filename(file.filename)
        upload_folder = get_folder(RELATIVE_UPLOAD)
        output_folder = get_folder(RELATIVE_OUTPUT)
        save_path = os.path.join(upload_folder, filename)
        file.save(save_path)

        # Read and check image
        image = cv2.imread(save_path)
        if image is None or image.size == 0:
            flash("Uploaded image is empty or unreadable.", "danger")
            return render_template('text_density.html')

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Preprocess for better OCR
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        resized = cv2.resize(enhanced, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
        thresh = cv2.adaptiveThreshold(
            resized, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 15, 9
        )

        # OCR
        custom_config = r'--oem 3 --psm 6'
        boxes = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT, config=custom_config)
        image_area = image.shape[0] * image.shape[1]

        # Draw text detections
        for i in range(len(boxes['text'])):
            text = boxes['text'][i].strip()
            conf = int(boxes['conf'][i])
            if text and conf >= 40:
                x, y, w, h = boxes['left'][i], boxes['top'][i], boxes['width'][i], boxes['height'][i]
                text_count += 1
                total_text_area += (w * h)

                # Scale back to original image size
                x, y, w, h = [int(val / 2) for val in (x, y, w, h)]
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Calculate ratio
        text_area_ratio = total_text_area / 4 / image_area if image_area > 0 else 0

        # Save overlay
        overlay_name = f"overlay_{filename}"
        overlay_path = os.path.join(output_folder, overlay_name)
        cv2.imwrite(overlay_path, image)

        # URLs for rendering
        image_url = url_for('static', filename=f'{RELATIVE_UPLOAD}/{filename}')
        overlay_url = url_for('static', filename=f'{RELATIVE_OUTPUT}/{overlay_name}')

        # Recommendations
        if text_count == 0:
            recommendation = "⚠️ No text detected. Use bold titles for better visibility."
        elif text_count > 20:
            recommendation = "⚠️ Too much text. Simplify your message."
        elif text_area_ratio > 0.3:
            recommendation = "⚠️ High text coverage. Reduce visual clutter."
        else:
            recommendation = "✅ Text density looks optimal."

    return render_template(
        'text_density.html',
        image_url=image_url,
        overlay_url=overlay_url,
        text_count=text_count,
        recommendation=recommendation
    )
