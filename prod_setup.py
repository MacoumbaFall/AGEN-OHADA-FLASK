from app import create_app, db
from app.models import User, TypeActe, TypeFormalite, Formalite
from app.comptabilite.service import ComptabiliteService
import os
import sys
from pathlib import Path
from sqlalchemy import text

def setup():
    app = create_app()
    with app.app_context():
        print("--- Step 1: Creating Tables ---")
        db.create_all()
        
        # Manual migration for formalites.type_id if not created by create_all
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE formalites ADD COLUMN IF NOT EXISTS type_id INTEGER REFERENCES type_formalites(id)"))
                conn.commit()
            print("Info: Column type_id verified/added.")
        except Exception as e:
            print(f"Info: type_id addition note: {e}")

        print("Success: Tables created/verified.")

        print("\n--- Step 2: Creating Admin User ---")
        admin = db.session.scalar(db.select(User).where(User.username == 'admin'))
        if not admin:
            admin_pwd = os.environ.get('ADMIN_PASSWORD', 'admin123')
            admin = User(username='admin', email='admin@example.com', role='ADMIN')
            admin.set_password(admin_pwd)
            db.session.add(admin)
            db.session.commit()
            print(f"Success: Admin user created (Pwd: {admin_pwd})")
        else:
            print("Info: Admin user already exists.")

        print("\n--- Step 3: Initializing Act Types ---")
        if db.session.query(TypeActe).count() == 0:
            defaults = [
                ('VENTE', 'Vente Immobilière'),
                ('PROCURATION', 'Procuration'),
                ('CONTRAT', 'Contrat Divers'),
                ('TESTAMENT', 'Testament'),
                ('SURETE', 'Sûreté / Hypothèque'),
                ('DIVERS', 'Autre')
            ]
            for nom, desc in defaults:
                db.session.add(TypeActe(nom=nom, description=desc))
            db.session.commit()
            print("Success: Act types initialized.")
        else:
            print("Info: Act types already exist.")

        print("\n--- Step 4: Initializing Formality Types ---")
        if db.session.query(TypeFormalite).count() == 0:
            default_formalites = [
                ('ENREGISTREMENT IMPÔTS', 'Enregistrement Impôts', 25000, 3),
                ('INSCRIPTION HYPOTHÉCAIRE', 'Inscription Hypothécaire', 50000, 15),
                ('DÉPÔT RCCM', 'Dépôt RCCM', 30000, 5),
                ('PUBLICATION JOURNAL OFFICIEL', 'Publication Journal Officiel', 15000, 7),
                ('FORMALITÉS CADASTRALES', 'Formalités Cadastrales', 40000, 20),
                ('DIVERS', 'Autre', 0, 1)
            ]
            for nom, desc, cout, delai in default_formalites:
                db.session.add(TypeFormalite(nom=nom, description=desc, cout_base=cout, delai_moyen=delai))
            db.session.commit()
            print("Success: Formality types initialized.")
        else:
            print("Info: Formality types already exist.")

        print("\n--- Step 5: Initializing Accounting Accounts ---")
        try:
            ComptabiliteService.initialize_default_accounts()
            print("Success: Accounting chart initialized.")
        except Exception as e:
            print(f"Warning: Accounting init skipped or already done: {e}")

        print("\n" + "="*30)
        print("DATABASE SETUP COMPLETE!")
        print("="*30)

if __name__ == "__main__":
    setup()
