from flask import Blueprint

bp = Blueprint('actes', __name__)

from app.actes import routes
