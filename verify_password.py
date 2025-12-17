from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    u = db.session.scalar(db.select(User).where(User.username == 'admin'))
    if u:
        print(f"User found: {u.username}")
        # Test password
        is_valid = u.check_password('admin')
        print(f"Password 'admin' is valid: {is_valid}")
    else:
        print("User 'admin' does not exist.")
