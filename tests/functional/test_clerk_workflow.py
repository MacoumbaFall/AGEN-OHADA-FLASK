import pytest
from app import db
from app.models import Client, Dossier, TypeActe, Acte
from decimal import Decimal

def test_full_clerk_workflow(client, auth, app):
    """
    Simulate a full clerk workflow:
    1. Login
    2. Create Client
    3. Create Dossier
    4. Calculate Provision for Vente
    5. Save Provision as Note
    """
    # 1. Login
    auth.login()
    
    with app.app_context():
        # Ensure TypeActe 'Vente' exists
        ta = db.session.scalar(db.select(TypeActe).where(TypeActe.nom == 'Vente'))
        if not ta:
            ta = TypeActe(nom='Vente', description='Vente Immobilière')
            db.session.add(ta)
            db.session.commit()

    # 2. Create Client
    response = client.post('/clients/new', data={
        'type_client': 'PHYSIQUE',
        'nom': 'SOW',
        'prenom': 'Abdou',
        'email': 'sow@example.com',
        'telephone': '771234567'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"SOW" in response.data

    # 3. Create Dossier
    with app.app_context():
        c = db.session.scalar(db.select(Client).where(Client.nom == 'SOW'))
        client_id = c.id

    response = client.post('/dossiers/new', data={
        'numero_dossier': 'DOS-TEST-001',
        'intitule': 'Vente Villa Malika',
        'type_dossier': 'VENTE',
        'statut': 'OUVERT',
        'responsable_id': 1
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Vente Villa Malika" in response.data

    # 4. Access Barème for Vente
    # We need the ID of the TypeActe 'Vente'
    with app.app_context():
        ta = db.session.scalar(db.select(TypeActe).where(TypeActe.nom == 'Vente'))
        type_id = ta.id
        d = db.session.scalar(db.select(Dossier).where(Dossier.intitule == 'Vente Villa Malika'))
        dossier_id = d.id

    # 5. Simulate Calculation (POST to bareme_generic)
    # The slug for Vente is 'vente'
    response = client.post(f'/actes/bareme/vente?type_id={type_id}&dossier_id={dossier_id}', data={
        'action': 'calculate',
        'prix': '100000000',
        'taux_enregistrement': '10',
        'morcellement': 'on'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # 100M * 10% = 10,000,000
    assert b"10,000,000" in response.data 

    # 6. Save Provision
    # This creates a 'NOTE DE PROVISION' Acte
    response = client.post(f'/actes/bareme/vente?type_id={type_id}&dossier_id={dossier_id}', data={
        'action': 'save',
        'prix': '100000000',
        'taux_enregistrement': '10',
        'morcellement': 'on',
        'dossier_id': dossier_id
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"NOTE DE PROVISION" in response.data

    # 7. Verify Acte in DB
    with app.app_context():
        acte = db.session.scalar(db.select(Acte).where(Acte.dossier_id == dossier_id))
        assert acte is not None
        assert acte.type_acte == 'NOTE DE PROVISION'
        assert acte.contenu_json['result']['total_general'] > 10000000 # Enregistrement + Honoraires + etc.
