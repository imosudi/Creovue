import os
import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from flask import Blueprint, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename

colour_bp = Blueprint('colour_heatmap', __name__, template_folder='templates', static_folder='static')

UPLOAD_FOLDER = 'static/uploads'
HEATMAP_FOLDER = 'static/heatmaps'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

#sudo mkdir -p /home/mosud/dev/Creovue/Creovue/thumbnail_eval/static
try:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
except :
    pass

try:
    os.makedirs(HEATMAP_FOLDER, exist_ok=True)
except :
    pass



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@colour_bp.route('/thumbnail/colour-heatmap', methods=['GET', 'POST'])
def colour_heatmap():
    image_url = None
    heatmap_url = None

    if request.method == 'POST':
        file = request.files.get('thumbnail')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            # Load image and convert to heatmap
            image = cv2.imread(filepath)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            plt.figure(figsize=(6, 6))
            plt.imshow(gray, cmap='hot', interpolation='nearest')
            plt.axis('off')

            heatmap_filename = f"heatmap_{filename}.png"
            heatmap_path = os.path.join(HEATMAP_FOLDER, heatmap_filename)
            plt.savefig(heatmap_path, bbox_inches='tight', pad_inches=0)
            plt.close()

            image_url = url_for('colour_heatmap.static', filename=f'uploads/{filename}')
            heatmap_url = url_for('colour_heatmap.static', filename=f'heatmaps/{heatmap_filename}')
        else:
            flash('Invalid image format. Only PNG, JPG, JPEG supported.', 'danger')

    return render_template('colour_heatmap.html', image_url=image_url, heatmap_url=heatmap_url)
