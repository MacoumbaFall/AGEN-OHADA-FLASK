import markdown2
import os
from flask import render_template, current_app
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

@bp.route('/help')
@login_required
def help():
    manual_path = os.path.join(current_app.root_path, '..', 'MANUAL_UTILISATEUR.md')
    content = ""
    if os.path.exists(manual_path):
        with open(manual_path, 'r', encoding='utf-8') as f:
            content = f.read()
    
    html_content = markdown2.markdown(content, extras=["tables", "fenced-code-blocks", "toc"])
    return render_template('main/help.html', title='Aide en ligne', content=html_content)
