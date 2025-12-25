from app import create_app, db
from sqlalchemy import text
import sys

def migrate():
    # Capture DATABASE_URL from command line if provided
    if len(sys.argv) > 1:
        import os
        os.environ['DATABASE_URL'] = sys.argv[1]
        print(f"Using DATABASE_URL from command line.")

    app = create_app()
    with app.app_context():
        print("--- Starting Production Schema Migration v2 ---")
        try:
            # --- Table 'templates' ---
            print("Updating 'templates' table...")
            db.session.execute(text("ALTER TABLE templates ADD COLUMN IF NOT EXISTS file_path VARCHAR(255)"))
            db.session.execute(text("ALTER TABLE templates ADD COLUMN IF NOT EXISTS is_docx BOOLEAN DEFAULT FALSE"))
            db.session.execute(text("ALTER TABLE templates ADD COLUMN IF NOT EXISTS type_acte_id INTEGER REFERENCES type_actes(id)"))
            db.session.execute(text("ALTER TABLE templates ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"))
            db.session.execute(text("ALTER TABLE templates ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"))

            # --- Table 'actes' ---
            print("Updating 'actes' table...")
            db.session.execute(text("ALTER TABLE actes ADD COLUMN IF NOT EXISTS type_acte_id INTEGER REFERENCES type_actes(id)"))
            db.session.execute(text("ALTER TABLE actes ADD COLUMN IF NOT EXISTS contenu_json JSONB"))
            db.session.execute(text("ALTER TABLE actes ADD COLUMN IF NOT EXISTS contenu_html TEXT"))
            db.session.execute(text("ALTER TABLE actes ADD COLUMN IF NOT EXISTS finalise_par_id INTEGER REFERENCES users(id)"))
            db.session.execute(text("ALTER TABLE actes ADD COLUMN IF NOT EXISTS date_finalisation TIMESTAMP WITH TIME ZONE"))
            db.session.execute(text("ALTER TABLE actes ADD COLUMN IF NOT EXISTS signature_electronique TEXT"))
            db.session.execute(text("ALTER TABLE actes ADD COLUMN IF NOT EXISTS numero_repertoire INTEGER"))
            db.session.execute(text("ALTER TABLE actes ADD COLUMN IF NOT EXISTS date_archivage TIMESTAMP WITH TIME ZONE"))
            db.session.execute(text("ALTER TABLE actes ADD COLUMN IF NOT EXISTS archive_par_id INTEGER REFERENCES users(id)"))
            db.session.execute(text("ALTER TABLE actes ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"))

            db.session.commit()
            print("--- Migration Successful! ---")
        except Exception as e:
            db.session.rollback()
            print(f"!!! Error during migration: {e}")
            sys.exit(1)

if __name__ == "__main__":
    migrate()
