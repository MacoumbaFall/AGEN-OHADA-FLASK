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


@click.command('seed-parametres')
@with_appcontext
def seed_parametres():
    """Initialise les param\u00e8tres de l'\u00e9tude avec les valeurs par d\u00e9faut."""
    from app.actes.services.parametres import ParametreService
    created = ParametreService.seed_defaults()
    if created:
        print(f'{created} param\u00e8tre(s) cr\u00e9\u00e9(s) avec succ\u00e8s.')
    else:
        print('Tous les param\u00e8tres sont d\u00e9j\u00e0 pr\u00e9sents en base. Aucun changement.')


def register(app):
    app.cli.add_command(create_admin)
    app.cli.add_command(seed_parametres)
