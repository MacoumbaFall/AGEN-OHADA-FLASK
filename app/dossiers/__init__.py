from flask import Blueprint

bp = Blueprint('dossiers', __name__)

from app.dossiers import routes
