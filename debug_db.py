from app import create_app, db
from app.models import TypeActe, Template

app = create_app()
with app.app_context():
    types = db.session.execute(db.select(TypeActe)).scalars().all()
    templates = db.session.execute(db.select(Template)).scalars().all()
    
    print(f"Number of TypeActe: {len(types)}")
    for t in types:
        print(f" - ID: {t.id}, Nom: {t.nom}")
        
    print(f"Number of Templates: {len(templates)}")
    for t in templates:
        print(f" - ID: {t.id}, Nom: {t.nom}")
