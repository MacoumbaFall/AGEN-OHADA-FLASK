import pytest
from app.models import Dossier, User
from app import db

def test_formalites_index(client, auth):
    auth.login()
    response = client.get('/formalites/')
    assert response.status_code == 200
    assert b'Formalit\xc3\xa9s' in response.data or b'recherche_formalites' in response.data # Check for title or search bar ID

def test_create_formalite(client, auth, app):
    auth.login()
    dossier_id = None
    
    with app.app_context():
        user = db.session.execute(db.select(User).filter_by(username='admin')).scalar_one()
        dossier = Dossier(
            numero_dossier='DOS-FORM-01', 
            intitule='Dossier Formalite Test', 
            responsable_id=user.id,
            type_dossier='VENTE'
        )
        db.session.add(dossier)
        db.session.commit()
        dossier_id = dossier.id

    response = client.post('/formalites/new', data={
        'dossier': dossier_id,
        'type_formalite': 'ENREGISTREMENT',
        'statut': 'A_FAIRE',
        'cout_estime': '50000',
        'submit': 'Enregistrer'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Formalit\xc3\xa9 cr\xc3\xa9\xc3\xa9e' in response.data or b'avec success' in response.data
    assert b'ENREGISTREMENT' in response.data
    assert b'DOS-FORM-01' in response.data
