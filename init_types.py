from app import create_app, db
from app.models import TypeActe

app = create_app()

def init_types():
    with app.app_context():
        # Check if types already exist
        count = db.session.query(TypeActe).count()
        if count == 0:
            defaults = [
                ('VENTE', 'Vente Immobilière'),
                ('PROCURATION', 'Procuration'),
                ('CONTRAT', 'Contrat Divers'),
                ('TESTAMENT', 'Testament'),
                ('SURETE', 'Sûreté / Hypothèque'),
                ('DIVERS', 'Autre')
            ]
            for nom, desc in defaults:
                ta = TypeActe(nom=nom, description=desc)
                db.session.add(ta)
            db.session.commit()
            print("Default act types initialized.")
        else:
            print("Act types already initialized.")

if __name__ == '__main__':
    init_types()
