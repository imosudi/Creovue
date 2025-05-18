# Creovue/thumbnail/colour_heatmap.py

import os
import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify, current_app
from werkzeug.utils import secure_filename

colour_bp = Blueprint('colour_heatmap', __name__, template_folder='templates', static_folder='static')

UPLOAD_FOLDER = '/uploads' #'static/uploads'
HEATMAP_FOLDER = '/heatmaps' #'static/heatmaps'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(HEATMAP_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Main route (template-based)
@colour_bp.route('/thumbnail/colour-heatmap', methods=['GET', 'POST'])
def colour_heatmap():
    image_url = None
    heatmap_url = None

    if request.method == 'POST':
        file = request.files.get('thumbnail')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            abs_upload_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
            abs_heatmap_path = os.path.join(current_app.root_path, HEATMAP_FOLDER)

            os.makedirs(abs_upload_path, exist_ok=True)
            os.makedirs(abs_heatmap_path, exist_ok=True)

            filepath = os.path.join(abs_upload_path, filename)
            file.save(filepath)

            # Convert to heatmap
            image = cv2.imread(filepath)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            plt.figure(figsize=(6, 6))
            plt.imshow(gray, cmap='hot', interpolation='nearest')
            plt.axis('off')

            name, _ = os.path.splitext(filename)
            heatmap_filename = f"heatmap_{name}.png"
            heatmap_path = os.path.join(abs_heatmap_path, heatmap_filename)
            plt.savefig(heatmap_path, bbox_inches='tight', pad_inches=0)
            plt.close()

            image_url = url_for('colour_heatmap.static', filename=f'uploads/{filename}')
            heatmap_url = url_for('colour_heatmap.static', filename=f'heatmaps/{heatmap_filename}')
        else:
            flash('Invalid image format. Only PNG, JPG, JPEG supported.', 'danger')

    return render_template('colour_heatmap.html', image_url=image_url, heatmap_url=heatmap_url)


# ✅ API route (JSON-based response)
@colour_bp.route('/api/colour-heatmap', methods=['POST'])
def colour_heatmap_api():
    file = request.files.get('thumbnail')
    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Unsupported or missing file'}), 400

    filename = secure_filename(file.filename)
    abs_upload_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
    abs_heatmap_path = os.path.join(current_app.root_path, HEATMAP_FOLDER)

    os.makedirs(abs_upload_path, exist_ok=True)
    os.makedirs(abs_heatmap_path, exist_ok=True)

    filepath = os.path.join(abs_upload_path, filename)
    file.save(filepath)

    # Convert to grayscale and heatmap
    image = cv2.imread(filepath)
    if image is None:
        return jsonify({'error': 'Failed to process image'}), 500

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    plt.figure(figsize=(6, 6))
    plt.imshow(gray, cmap='hot', interpolation='nearest')
    plt.axis('off')

    name, _ = os.path.splitext(filename)
    heatmap_filename = f"heatmap_{name}.png"
    heatmap_path = os.path.join(abs_heatmap_path, heatmap_filename)
    plt.savefig(heatmap_path, bbox_inches='tight', pad_inches=0)
    plt.close()

    image_url = url_for('static', filename=f'uploads/{filename}', _external=True)
    heatmap_url = url_for('static', filename=f'heatmaps/{heatmap_filename}', _external=True)

    return jsonify({
        'original_image': image_url,
        'heatmap_image': heatmap_url,
        'message': 'Heatmap generated successfully'
    })
