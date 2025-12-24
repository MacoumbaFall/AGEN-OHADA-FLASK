import os
import sys

# Add the current directory to sys.path to find 'app'
sys.path.append(os.getcwd())

from app import create_app, db
from app.models import Template, TypeActe

app = create_app()
with app.app_context():
    try:
        # Get the first TypeActe
        ta = db.session.scalar(db.select(TypeActe))
        if not ta:
            print("ERROR: No TypeActe found")
            sys.exit(1)
            
        print(f"Using TypeActe: {ta.nom} (ID: {ta.id})")
        
        # Attempt to create a template
        new_template = Template(
            nom="Script Test Template",
            type_acte_id=ta.id,
            description="Created by debug script",
            contenu="# Test Content\nThis is a test."
        )
        db.session.add(new_template)
        db.session.commit()
        print(f"SUCCESS: Template created with ID {new_template.id}")
        
        # Clean up
        db.session.delete(new_template)
        db.session.commit()
        print("Cleaned up test template.")
        
    except Exception as e:
        print(f"FAILED: {str(e)}")
        db.session.rollback()
