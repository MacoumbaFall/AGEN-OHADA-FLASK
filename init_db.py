from app import create_app, db
from app.models import User
import os

def init_db():
    print("Initializing database...")
    
    # Create app with current environment config
    app = create_app()
    
    with app.app_context():
        # Force create all tables (safe - won't drop existing tables)
        print("Creating database tables...")
        db.create_all()
        print("Tables created/verified.")
        
        # Check/Create Admin User
        admin = db.session.scalar(db.select(User).where(User.username == 'admin'))
        if not admin:
            print("Creating 'admin' user...")
            # Get default password from env or use 'admin'
            admin_pwd = os.environ.get('ADMIN_PASSWORD', 'admin')
            admin = User(username='admin', email='admin@example.com', role='ADMIN')
            admin.set_password(admin_pwd)
            db.session.add(admin)
            db.session.commit()
            print(f"Admin user created with password: {admin_pwd}")
        else:
            print("Admin user already exists.")

if __name__ == "__main__":
    init_db()
