import pytest
from app.models import Dossier, Template, User
from app import db

def test_templates_index(client, auth):
    auth.login()
    response = client.get('/actes/templates')
    assert response.status_code == 200
    assert b'Mod\xc3\xa8les' in response.data or b'Mod\xe8les' in response.data

def test_template_create(client, auth):
    auth.login()
    response = client.post('/actes/templates/new', data={
        'nom': 'Template Test',
        'type_acte': 'VENTE',
        'description': 'Description Test',
        'contenu': '<p>Contenu Test {{ dossier.intitule }}</p>',
        'submit': 'Enregistrer'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Mod\xc3\xa8le cr\xc3\xa9\xc3\xa9' in response.data or b'avec success' in response.data
    assert b'Template Test' in response.data

def test_act_generation(client, auth, app):
    auth.login()
    dossier_id = None
    template_id = None
    
    with app.app_context():
        # Setup Data
        user = db.session.execute(db.select(User).filter_by(username='admin')).scalar_one()
        
        dossier = Dossier(
            numero_dossier='DOS-ACTE-01', 
            intitule='Dossier Acte Test', 
            responsable_id=user.id,
            type_dossier='VENTE'
        )
        db.session.add(dossier)
        
        template = Template(
            nom='Template Vente Test',
            type_acte='VENTE',
            contenu='<h1>Acte de Vente</h1><p>Dossier: {{ dossier.numero_dossier }}</p>'
        )
        db.session.add(template)
        db.session.commit()
        
        dossier_id = dossier.id
        template_id = template.id

    # Test Generate Preview
    response = client.post('/actes/generate', data={
        'dossier': dossier_id,
        'template': template_id,
        'submit': 'Pr\xc3\xa9visualiser' # submit button name
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Check preview content
    assert b'Acte de Vente' in response.data
    assert b'DOS-ACTE-01' in response.data
    assert b'G\xc3\xa9n\xc3\xa9ration r\xc3\xa9ussie' in response.data or b'ration r\xc3\xa9ussie' in response.data

    # Test Generate and Save
    response_save = client.post('/actes/generate', data={
        'dossier': dossier_id,
        'template': template_id,
        'save': 'Valider et Sauvegarder' # save button name
    }, follow_redirects=True)
    
    assert response_save.status_code == 200
    assert b'Acte sauvegard\xc3\xa9' in response_save.data
    assert b'D\xc3\xa9tails de l\'Acte' in response_save.data or b'Acte' in response_save.data
