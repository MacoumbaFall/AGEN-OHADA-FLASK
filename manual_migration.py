from app import create_app, db
from sqlalchemy import text

def migrate():
    app = create_app()
    with app.app_context():
        print("Starting manual migration for templates table...")
        try:
            # Check if columns exist first (optional but safer)
            db.session.execute(text("ALTER TABLE templates ADD COLUMN IF NOT EXISTS file_path VARCHAR(255)"))
            db.session.execute(text("ALTER TABLE templates ADD COLUMN IF NOT EXISTS is_docx BOOLEAN DEFAULT FALSE"))
            
            # Also update 'contenu' to be nullable if it wasn't already (though handled in model)
            db.session.execute(text("ALTER TABLE templates ALTER COLUMN contenu DROP NOT NULL"))
            
            db.session.commit()
            print("Successfully added file_path and is_docx columns to templates table.")
        except Exception as e:
            db.session.rollback()
            print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate()
