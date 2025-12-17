import click
from flask.cli import with_appcontext
from app import db
from app.models import User

@click.command('create-admin')
@click.argument('username')
@click.argument('email')
@click.argument('password')
@with_appcontext
def create_admin(username, email, password):
    """Create an admin user."""
    if db.session.scalar(db.select(User).where(User.username == username)):
        print(f'User {username} already exists.')
        return
    
    user = User(username=username, email=email, role='ADMIN')
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    print(f'Admin user {username} created successfully.')

def register(app):
    app.cli.add_command(create_admin)
