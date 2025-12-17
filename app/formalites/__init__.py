from flask import Blueprint

bp = Blueprint('formalites', __name__)

from app.formalites import routes
