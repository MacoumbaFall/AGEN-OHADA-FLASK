import psycopg
from psycopg import sql
from app import create_app, db
from app.models import User
from app.config import Config

# 1. Create Database
def create_database():
    print("Connecting to 'postgres' database to create 'agen_ohada'...")
    try:
        # Connect to default 'postgres' db to create the target db
        # We need to parse the config URI to get credentials, or just hardcode as we know them
        # Config.SQLALCHEMY_DATABASE_URI is 'postgresql+psycopg://postgres:admin123@localhost:5432/agen_ohada'
        
        # Connection string for 'postgres' db
        conn_str = "dbname=postgres user=postgres password=admin123 host=localhost port=5432"
        
        with psycopg.connect(conn_str, autocommit=True) as conn:
            with conn.cursor() as cur:
                # Check if exists
                cur.execute("SELECT 1 FROM pg_database WHERE datname = 'agen_ohada'")
                if not cur.fetchone():
                    print("Creating database 'agen_ohada'...")
                    cur.execute("CREATE DATABASE agen_ohada")
                    print("Database created.")
                else:
                    print("Database 'agen_ohada' already exists.")
    except Exception as e:
        print(f"Error creating database: {e}")
        # If it fails, maybe it already exists or auth error, we'll see.

# 2. Init Schema and Seed Data
def init_schema_and_seed():
    print("Initializing schema and seeding data...")
    app = create_app()
    with app.app_context():
        # Create tables
        db.create_all()
        print("Tables created.")
        
        # Check/Create Admin User
        admin = db.session.scalar(db.select(User).where(User.username == 'admin'))
        if not admin:
            print("Creating 'admin' user...")
            admin = User(username='admin', email='admin@example.com', role='ADMIN')
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created.")
        else:
            print("Admin user already exists.")

if __name__ == "__main__":
    create_database()
    init_schema_and_seed()
