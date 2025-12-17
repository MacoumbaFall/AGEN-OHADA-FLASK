import pytest
from app.models import Client, User
from app import db

def test_clients_index(client, auth):
    auth.login()
    response = client.get('/clients')
    assert response.status_code == 200
    assert b'Clients' in response.data

def test_create_client_physique(client, auth):
    auth.login()
    response = client.post('/clients/new', data={
        'type_client': 'PHYSIQUE',
        'nom': 'Dupont',
        'prenom': 'Jean',
        'email': 'jean.dupont@example.com',
        'telephone': '0102030405',
        'submit': 'Enregistrer'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Client cr\xc3\xa9\xc3\xa9 avec succ\xc3\xa8s' in response.data or b'avec success' in response.data
    assert b'Dupont' in response.data
    assert b'Jean' in response.data

def test_create_client_morale(client, auth):
    auth.login()
    response = client.post('/clients/new', data={
        'type_client': 'MORALE',
        'nom': 'Societes SARL',
        'email': 'contact@societe.com',
        'telephone': '1122334455',
        'submit': 'Enregistrer'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Client cr\xc3\xa9\xc3\xa9' in response.data
    assert b'Societes SARL' in response.data
