from app import create_app, db
from app.models import ComptaCompte

app = create_app()
with app.app_context():
    comptes = db.session.execute(db.select(ComptaCompte).order_by(ComptaCompte.numero_compte)).scalars().all()
    for c in comptes:
        print(f"ID={c.id} Num={c.numero_compte} Libelle={c.libelle}")
