from app.models import User
from app import db

def test_login_page(client):
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Connexion' in response.data

def test_login_success(client, app):
    with app.app_context():
        # Use a different username to avoid conflict with conftest admin
        u = User(username='test_login_user', email='test_login@example.com', role='ADMIN')
        u.set_password('password')
        db.session.add(u)
        db.session.commit()

    response = client.post('/auth/login', data={
        'username': 'test_login_user',
        'password': 'password'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Tableau de Bord' in response.data
    assert b'Bienvenue, test_login_user !' in response.data

def test_login_failure(client, app):
    response = client.post('/auth/login', data={
        'username': 'admin',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Nom d&#39;utilisateur ou mot de passe invalide' in response.data or b'Nom d\'utilisateur ou mot de passe invalide' in response.data
