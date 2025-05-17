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
    image_url = None
    overlay_url = None
    text_count = 0
    text_area = 0

    # Filter out low-confidence detections
    min_conf = 40
    text_results = []
    filtered_texts = []
    total_text_area = 0

    if request.method == 'POST':
        file = request.files.get('thumbnail')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_folder = get_folder(RELATIVE_UPLOAD)
            output_folder = get_folder(RELATIVE_OUTPUT)
            save_path = os.path.join(upload_folder, filename)
            file.save(save_path)

            # Read and preprocess image
            image = cv2.imread(save_path)
            if image is None or image.size == 0:
                flash("Uploaded image is empty or unreadable.", "danger")
                return render_template('text_density.html')

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Enhance contrast
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)

            # Resize to improve OCR accuracy
            resized = cv2.resize(enhanced, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

            # Threshold to isolate text
            thresh = cv2.adaptiveThreshold(
                resized, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 15, 9
            )

            # OCR with config
            custom_config = r'--oem 3 --psm 6'
            boxes = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT, config=custom_config)

            # Draw bounding boxes and accumulate metrics
            for i in range(len(boxes['text'])):
                text = boxes['text'][i].strip()
                conf = int(boxes['conf'][i])
                if text and conf >= 40:
                    x, y, w, h = boxes['left'][i], boxes['top'][i], boxes['width'][i], boxes['height'][i]
                    cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    text_count += 1
                    text_area += w * h
            
            for i in range(len(boxes['text'])):
                if int(boxes['conf'][i]) >= min_conf:
                    if boxes['text'][i].strip():
                        text = boxes['text'][i]
                        conf = boxes['conf'][i]
                        box = (boxes['left'][i], boxes['top'][i], boxes['width'][i], boxes['height'][i])
                        
                        text_results.append({
                            'text': text,
                            'conf': conf,
                            'box': box
                        })
                        
                        filtered_texts.append(text)
                        
                        # Calculate text area for this detection
                        total_text_area += boxes['width'][i] * boxes['height'][i]
                        
                        # Draw bounding box on the overlay image
                        left, top, width, height = box
                        # Adjust coordinates back to original image scale
                        left = int(left / 2)
                        top = int(top / 2)
                        width = int(width / 2)
                        height = int(height / 2)
                        cv2.rectangle(image, (left, top), (left + width, top + height), (0, 255, 0), 2)
                        
                        # Add text label
                        cv2.putText(image, text, (left, top - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)


            
            # Count the number of detected text regions
            text_count = len(filtered_texts)
            print(f"Detected {text_count} text regions:", filtered_texts)

            # Calculate text area ratio
            text_area = total_text_area / 4  # Divide by 4 because we doubled both dimensions
            image_area = image.shape[0] * image.shape[1]
            text_area_ratio = text_area / image_area if image_area > 0 else 0

            # Save overlay
            overlay_name = f"overlay_{filename}"
            overlay_path = os.path.join(output_folder, overlay_name)
            cv2.imwrite(overlay_path, image)

            # URLs for frontend
            image_url = url_for('static', filename=f'{RELATIVE_UPLOAD}/{filename}')
            overlay_url = url_for('static', filename=f'{RELATIVE_OUTPUT}/{overlay_name}')

        else:
            flash('Invalid image format. Only PNG, JPG, JPEG supported.', 'danger')

    # Recommendation
    recommendation = ""
    if text_count == 0:
        recommendation = "⚠️ No text detected. Use bold titles for better visibility."
    elif text_count > 20:
        recommendation = "⚠️ Too much text. Simplify your message."
    elif image_url and overlay_url:
        height, width = image.shape[:2]
        coverage_ratio = text_area / (width * height)
        if coverage_ratio > 0.3:
            recommendation = "⚠️ High text coverage. Reduce visual clutter."
        else:
            recommendation = "✅ Text density looks optimal."
    else:
        recommendation = ""

    return render_template(
        'text_density.html',
        image_url=image_url,
        overlay_url=overlay_url,
        text_count=text_count,
        recommendation=recommendation
    )
