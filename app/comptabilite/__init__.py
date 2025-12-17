from flask import Blueprint

bp = Blueprint('comptabilite', __name__)

from app.comptabilite import routes
