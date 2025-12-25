from sqlalchemy import create_engine, text
import sys

def migrate(url):
    engine = create_engine(url)
    with engine.begin() as conn: # engine.begin() handles transaction and commit
        print("--- Surgical Migration Starting ---")
        
        # Templates
        try:
            print("Adding templates.file_path...")
            conn.execute(text("ALTER TABLE templates ADD COLUMN file_path VARCHAR(255)"))
            print("Done.")
        except Exception as e:
            print(f"Skipped templates.file_path: {e}")

        try:
            print("Adding templates.is_docx...")
            conn.execute(text("ALTER TABLE templates ADD COLUMN is_docx BOOLEAN DEFAULT FALSE"))
            print("Done.")
        except Exception as e:
            print(f"Skipped templates.is_docx: {e}")

        # Actes
        try:
            print("Adding actes.finalise_par_id...")
            conn.execute(text("ALTER TABLE actes ADD COLUMN finalise_par_id INTEGER REFERENCES users(id)"))
            print("Done.")
        except Exception as e:
            print(f"Skipped actes.finalise_par_id: {e}")

        try:
            print("Adding actes.date_finalisation...")
            conn.execute(text("ALTER TABLE actes ADD COLUMN date_finalisation TIMESTAMP WITH TIME ZONE"))
            print("Done.")
        except Exception as e:
            print(f"Skipped actes.date_finalisation: {e}")

        try:
            print("Adding actes.signature_electronique...")
            conn.execute(text("ALTER TABLE actes ADD COLUMN signature_electronique TEXT"))
            print("Done.")
        except Exception as e:
            print(f"Skipped actes.signature_electronique: {e}")

        print("--- Surgical Migration Finished ---")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python surgical_migrate.py <DATABASE_URL>")
        sys.exit(1)
    migrate(sys.argv[1])
