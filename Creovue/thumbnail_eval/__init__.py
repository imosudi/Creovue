# Creovue/thumbnail_eval/__init__.pytou 
from flask import Blueprint
from .face_detect import face_bp

thumbnail_eval_bp = Blueprint("thumbnail_eval", __name__, template_folder="templates", static_folder="static")

from . import routes



def register_thumbnail_eval(app):
    app.register_blueprint(face_bp)
