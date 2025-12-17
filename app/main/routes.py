from flask import render_template
from flask_login import login_required
from app.main import bp
from app import db
from app.models import Client, Dossier, Formalite
from sqlalchemy import func

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    # Fetch statistics
    stats = {
        'clients_count': db.session.scalar(db.select(func.count(Client.id))),
        'dossiers_active': db.session.scalar(db.select(func.count(Dossier.id)).filter(Dossier.statut != 'CLOTURE')),
        'formalites_pending': db.session.scalar(db.select(func.count(Formalite.id)).filter(Formalite.statut.in_(['A_FAIRE', 'EN_COURS']))),
        'dossiers_total': db.session.scalar(db.select(func.count(Dossier.id)))
    }
    
    return render_template('index.html', title='Tableau de Bord', stats=stats)
