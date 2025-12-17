from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from app.config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Veuillez vous connecter pour accéder à cette page.'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Context processors
    @app.context_processor
    def inject_now():
        from datetime import datetime
        return {'now': datetime.utcnow()}

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    # Register Blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.clients import bp as clients_bp
    app.register_blueprint(clients_bp)

    from app.dossiers import bp as dossiers_bp
    app.register_blueprint(dossiers_bp, url_prefix='/dossiers')

    from app.actes import bp as actes_bp
    app.register_blueprint(actes_bp, url_prefix='/actes')

    from app.formalites import bp as formalites_bp
    app.register_blueprint(formalites_bp, url_prefix='/formalites')

    from app.comptabilite import bp as comptabilite_bp
    app.register_blueprint(comptabilite_bp, url_prefix='/comptabilite')

    from app import cli
    cli.register(app)

    return app
