from app import create_app, db
from sqlalchemy import text

def migrate():
    app = create_app()
    with app.app_context():
        print("Starting manual migration for archiving system...")
        try:
            # Add columns to 'actes' table
            db.session.execute(text("ALTER TABLE actes ADD COLUMN IF NOT EXISTS numero_repertoire INTEGER"))
            db.session.execute(text("ALTER TABLE actes ADD COLUMN IF NOT EXISTS date_archivage TIMESTAMP WITH TIME ZONE"))
            db.session.execute(text("ALTER TABLE actes ADD COLUMN IF NOT EXISTS archive_par_id INTEGER REFERENCES users(id)"))
            
            db.session.commit()
            print("Successfully updated 'actes' table with archiving fields.")
        except Exception as e:
            db.session.rollback()
            print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate()
