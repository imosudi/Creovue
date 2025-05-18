# Creovue/thumbnail/__init__.pytou 
from flask import Blueprint
from .face_detect import face_bp
from .colour_heatmap import colour_bp
from .text_density import text_bp
from .ctr_predict import ctr_bp
from .evaluation_chain import eval_chain_bp

thumbnail_eval_bp = Blueprint("thumbnail", __name__, template_folder="templates", static_folder="static")

from . import routes

def register_thumbnail_routes(app):
    app.register_blueprint(face_bp)
    app.register_blueprint(colour_bp)
    app.register_blueprint(text_bp)
    app.register_blueprint(ctr_bp)
    app.register_blueprint(eval_chain_bp)


def register_thumbnail_eval(app):
    #app.register_blueprint(face_bp)
    pass