import pytest
from app.models import Dossier, Client, User
from app import db

def test_dossiers_index(client, auth):
    auth.login()
    response = client.get('/dossiers/')
    assert response.status_code == 200
    assert b'Dossiers' in response.data

def test_create_dossier(client, auth, app):
    auth.login()
    user_id = 1
    with app.app_context():
        user = db.session.execute(db.select(User).filter_by(username='admin')).scalar_one()
        user_id = user.id

    response = client.post('/dossiers/new', data={
        'numero_dossier': 'DOS-001',
        'intitule': 'Dossier Test Vente',
        'type_dossier': 'VENTE',
        'statut': 'OUVERT',
        'responsable_id': user_id
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Dossier cr\xc3\xa9\xc3\xa9 avec succ\xc3\xa8s' in response.data or b'avec success' in response.data
    assert b'DOS-001' in response.data

def test_add_party_to_dossier(client, auth, app):
    auth.login()
    dossier_id = None
    client_id = None
    
    with app.app_context():
        # Ensure we have a user, client and dossier
        user = db.session.execute(db.select(User).filter_by(username='admin')).scalar_one()
        
        client_obj = Client(nom='Doe', prenom='John', type_client='PHYSIQUE')
        db.session.add(client_obj)
        
        dossier = Dossier(
            numero_dossier='DOS-PARTY-01', 
            intitule='Dossier Party Test', 
            responsable_id=user.id,
            type_dossier='VENTE'
        )
        db.session.add(dossier)
        db.session.commit()
        
        dossier_id = dossier.id
        client_id = client_obj.id

    # Add party
    response = client.post(f'/dossiers/{dossier_id}', data={
        'client_id': client_id,
        'role_dans_acte': 'VENDEUR'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Partie ajout\xc3\xa9e' in response.data
    assert b'Doe' in response.data
    assert b'VENDEUR' in response.data

def test_edit_dossier(client, auth, app):
    auth.login()
    dossier_id = None
    user_id = None
    
    with app.app_context():
        user = db.session.execute(db.select(User).filter_by(username='admin')).scalar_one()
        user_id = user.id
        
        dossier = Dossier(
            numero_dossier='DOS-EDIT-01', 
            intitule='Dossier Before Edit', 
            responsable_id=user.id,
            type_dossier='VENTE'
        )
        db.session.add(dossier)
        db.session.commit()
        dossier_id = dossier.id

    response = client.post(f'/dossiers/{dossier_id}/edit', data={
        'numero_dossier': 'DOS-EDIT-01-MOD',
        'intitule': 'Dossier After Edit',
        'type_dossier': 'SUCCESSION',
        'statut': 'EN_COURS',
        'responsable_id': user_id
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Dossier mis \xc3\xa0 jour' in response.data
    assert b'DOS-EDIT-01-MOD' in response.data
    assert b'SUCCESSION' in response.data
