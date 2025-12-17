from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    admin = db.session.scalar(db.select(User).where(User.username == 'admin'))
    if admin:
        print("Resetting admin password to 'admin'...")
        admin.set_password('admin')
        db.session.commit()
        print("Password reset successfully.")
    else:
        print("Admin user not found. Creating...")
        admin = User(username='admin', email='admin@example.com', role='ADMIN')
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created.")
