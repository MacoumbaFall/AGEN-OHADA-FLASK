from app import create_app, db
from app.models import ComptaBareme

def migrate():
    app = create_app()
    with app.app_context():
        print("Creating ComptaBareme table...")
        try:
            db.create_all()
            db.session.commit()
            print("Successfully created/updated tables.")
        except Exception as e:
            db.session.rollback()
            print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate()
