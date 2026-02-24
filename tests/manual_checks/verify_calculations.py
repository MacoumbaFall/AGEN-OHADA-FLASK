from app import create_app, db
from app.models import User, TypeActe

print("Starting custom integration test...")
app = create_app()
app.config['WTF_CSRF_ENABLED'] = False

with app.app_context():
    print("App context pushed.")
    
    # 1. Setup Data
    try:
        user = db.session.execute(db.select(User).filter_by(username='test_notaire')).scalar_one_or_none()
        if not user:
            print("Creating test user...")
            user = User(username='test_notaire', email='test@test.com', role='NOTAIRE')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
        else:
            print("Test user found.")

        ta = db.session.execute(db.select(TypeActe).filter_by(nom='VENTE')).scalar_one_or_none()
        if not ta:
             print("Creating TypeActe VENTE...")
             ta = TypeActe(nom='VENTE', description='Vente test')
             db.session.add(ta)
             db.session.commit()
    except Exception as e:
        print(f"Data setup error: {e}")
        db.session.rollback()

    # 2. Start Client
    client = app.test_client()

    # 3. Login
    print("Attempting login...")
    resp = client.post('/auth/login', data={'username': 'test_notaire', 'password': 'password'}, follow_redirects=True)
    if b'Tableau de bord' in resp.data or resp.status_code == 200:
        print("Login Successful.")
    else:
        print(f"Login Failed via POST. Status: {resp.status_code}")
        # print(resp.data.decode('utf-8')) # Too redundant

    # 4. Test Route GET
    print("Testing GET /actes/bareme/vente ...")
    resp_get = client.get('/actes/bareme/vente', follow_redirects=True)
    print(f"GET Status: {resp_get.status_code}")
    if resp_get.status_code == 200:
        print("GET Success.")
    else:
        print("GET Failed.")
        print(resp_get.data[:500]) # First 500 chars

    # 5. Test Calculation POST
    print("Testing POST Calculation...")
    data = {
        'action': 'calculate',
        'prix': '50000000',
        'taux_enregistrement': '10',
        'morcellement': ''
    }
    resp_post = client.post('/actes/bareme/vente', data=data, follow_redirects=True)
    print(f"POST Status: {resp_post.status_code}")
    
    # Check for specific calculation result (Emolument proportionnel)
    # The template renders "Émoluments" so we check for that substring (utf-8 bytes)
    if b'moluments' in resp_post.data: 
        print("SUCCESS: Calculation result found in response.")
    else:
        print("FAILURE: meaningful result not found in response.")
        # Save output for review
        with open('debug_response.html', 'wb') as f:
            f.write(resp_post.data)
        print("Response saved to debug_response.html")

print("Test finished.")
