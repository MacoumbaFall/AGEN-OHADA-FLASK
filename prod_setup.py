"""
Consolidated Production Database Initialization Script
Combines init_db, init_types, and migrate_phase5 logic.
"""
from app import create_app, db
from app.models import User, TypeActe
from app.comptabilite.service import ComptabiliteService
import os
import sys
from pathlib import Path

def setup():
    app = create_app()
    with app.app_context():
        print("--- Step 1: Creating Tables ---")
        db.create_all()
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

        print("\n--- Step 4: Initializing Accounting Accounts ---")
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
