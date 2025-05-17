# Creovue/thumbnail_eval/routes.py
import os
from flask import render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from . import thumbnail_eval_bp
from .utils import evaluate_thumbnail

UPLOAD_FOLDER = 'static/uploads'

@thumbnail_eval_bp.route("/thumbnail-eval", methods=["GET", "POST"])
def thumbnail_eval():
    score = None
    filename = None
    if request.method == "POST":
        if 'thumbnail' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        file = request.files['thumbnail']
        if file.filename == '':
            flash('No selected file', 'warning')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            file.save(filepath)
            score = evaluate_thumbnail(filepath)
            return render_template("thumbnail_eval/result.html", score=score, image=url_for('static', filename=f"uploads/{filename}"))
    return render_template("thumbnail_eval/form.html")
