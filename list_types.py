from app import create_app, db
from app.models import TypeActe

app = create_app()
with app.app_context():
    types = db.session.execute(db.select(TypeActe)).scalars().all()
    for t in types:
        print(f"{t.id}: {t.nom}")
