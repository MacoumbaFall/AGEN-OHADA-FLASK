from app.models import User, Client, Dossier

def test_user_creation(app):
    user = User(username='testuser', email='test@example.com', role='ADMIN')
    user.set_password('cat')
    assert user.username == 'testuser'
    assert user.check_password('cat')
    assert not user.check_password('dog')

def test_client_creation(app):
    client = Client(type_client='PHYSIQUE', nom='Dupont', prenom='Jean')
    assert client.nom == 'Dupont'
    assert client.type_client == 'PHYSIQUE'

def test_dossier_creation(app):
    dossier = Dossier(numero_dossier='2025-01-001', intitule='Vente Maison')
    assert dossier.numero_dossier == '2025-01-001'
