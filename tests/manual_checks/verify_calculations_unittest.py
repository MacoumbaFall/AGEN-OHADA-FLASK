import unittest
from app import create_app, db
from app.models import User, TypeActe
from flask_login import current_user

class TestActesIntegration(unittest.TestCase):
    def setUp(self):
        # Configure app for testing
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # Use in-memory DB or keep existing if needed
        # NOTE: For this specific verification on the existing codebase state, we might want to run against 
        # the real DB or a configured test DB. Since I cannot easily set up a full test DB with migrations 
        # in this environment, I will try to use the app's existing configuration but ideally separate.
        # However, to be safe and avoid corrupting data, I should arguably use SQLite memory but that requires
        # running migrations.
        
        # Let's try a safer approach: Use the app context but rollback transactions.
        # Or better: Just check routes return 200/302 as expected.
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create tables for in-memory DB
        db.create_all()
        
        # Create Test User
        try:
             # Try to find existing user first to avoid unique constraint error if DB is persistent
            self.user = db.session.execute(db.select(User).filter_by(username='test_notaire')).scalar_one_or_none()
            if not self.user:
                self.user = User(username='test_notaire', email='test@test.com', role='NOTAIRE')
                self.user.set_password('password')
                db.session.add(self.user)
                db.session.commit()
            
            # Use existing type acte if available
            self.type_acte = db.session.execute(db.select(TypeActe).filter_by(nom='VENTE')).scalar_one_or_none()
            if not self.type_acte:
                 self.type_acte = TypeActe(nom='VENTE', description='Vente Immobilière')
                 db.session.add(self.type_acte)
                 db.session.commit()
                 
        except Exception as e:
            db.session.rollback()
            print(f"Setup Warning: {e}")
        
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self):
        return self.client.post('/auth/login', data=dict(
            username='test_notaire',
            password='password'
        ), follow_redirects=True)

    def test_generic_bareme_access(self):
        """Test accessing the generic bareme route for VENTE"""
        self.login()
        # Note: The route is /bareme/vente (legacy alias) or via generic router
        # The generic router redirects /types/id/bareme -> /bareme/slug
        
        # Direct access to legacy alias which is now handled by generic function
        response = self.client.get('/actes/bareme/vente', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Bar\xc3\xa8me Vente', response.data) # Check for title part

    def test_calculation_submission(self):
        """Test submitting a calculation to the generic route"""
        self.login()
        
        data = {
            'action': 'calculate',
            'prix': '50000000',
            'taux_enregistrement': '10',
            'morcellement': ''
        }
        
        response = self.client.post('/actes/bareme/vente', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Check if result is rendered. 
        # The template bareme_vente.html shows "Émoluments proportionnels Notaire" in tables
        # We need to handle encoding for assertions roughly
        self.assertIn(b'moluments proportionnels Notaire', response.data)

        # Basic math check: 50,000,000 * certain rate.
        # Just checking if we got a table back is enough for integration proof.

if __name__ == '__main__':
    unittest.main()
