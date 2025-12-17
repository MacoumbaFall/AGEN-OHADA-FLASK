from app.models import Recu, Facture, ComptaCompte

def test_comptabilite_access_protected(client):
    """Test that comptabilite routes are protected."""
    response = client.get('/comptabilite/')
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']

def test_dashboard_access_authorized(client, auth):
    """Test dashboard access for logged in user."""
    response = auth.login()
    assert b'Tableau de Bord' in response.data or b'Bienvenue' in response.data, f"Login failed: {response.data}"
    
    response = client.get('/comptabilite/')
    assert response.status_code == 200
    # "Tableau de bord" is lowercase 'b' in the p tag description 
    # Or check for h1 "Comptabilité" which is definitely there
    assert b'Comptabilit' in response.data

def test_create_account(client, auth, app):
    """Test creating a new accounting account."""
    auth.login()
    
    # Create account
    response = client.post('/comptabilite/comptes/new', data={
        'numero_compte': '411TEST',
        'libelle': 'Test Client Account',
        'type_compte': 'CLIENT',
        'categorie': 'CLIENT',
        'actif': 'True',
        'submit_btn': 'Enregistrer'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Check for flash message - simplified check
    assert b'avec succ' in response.data
    
    # Verify in DB
    with app.app_context():
        compte = ComptaCompte.query.filter_by(numero_compte='411TEST').first()
        assert compte is not None
        assert compte.libelle == 'Test Client Account'

def test_create_receipt(client, auth, app):
    """Test creating a receipt."""
    auth.login()
    
    # Create a client dossier/account setup if needed, but for now just basic receipt
    # Note: Recu creation relies on existing accounts. 
    # Conftest initializes DB but might not run 'initialize_default_accounts' from service unless we call it.
    # However, create_app usually doesn't auto-init data.
    # We should initialize accounts first.
    
    from app.comptabilite.service import ComptabiliteService
    with app.app_context():
        ComptabiliteService.initialize_default_accounts()
    
    response = client.post('/comptabilite/recus/new', data={
        'date_emission': '2025-01-01',
        'montant': '50000',
        'mode_paiement': 'ESPECES',
        'motif': 'Test Receipt',
        'reference_paiement': 'REF001',
        'submit_btn': 'Émettre le Reçu'  # Assuming utf-8 handling
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Check for success message or redirect to view
    assert b'Recu REC-' in response.data or b'Test Receipt' in response.data

