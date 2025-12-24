import os
import sys

# Add the current directory to sys.path to find 'app'
sys.path.append(os.getcwd())

from app import create_app, db
from app.models import TypeActe

app = create_app()
with app.app_context():
    try:
        types = db.session.scalars(db.select(TypeActe)).all()
        print(f"DEBUG: Found {len(types)} Types d'Acte")
        for t in types:
            print(f"- {t.nom}")
    except Exception as e:
        print(f"ERROR: {str(e)}")
