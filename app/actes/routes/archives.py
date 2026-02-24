from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from app import db
from app.actes import bp
from app.models import Dossier, Acte
from app.decorators import role_required
from datetime import datetime
import shutil
from pathlib import Path

# --- ARCHIVAGE ET RÉPERTOIRE ---

@bp.route('/repertoire')
@login_required
@role_required('NOTAIRE', 'CLERC', 'ADMIN')
def repertoire_index():
    # Formal Notarial Index: Only archived acts
    archived_acts = db.session.scalars(
        db.select(Acte).filter(Acte.numero_repertoire != None).order_by(Acte.numero_repertoire.desc())
    ).all()
    return render_template('actes/repertoire.html', actes=archived_acts)

@bp.route('/dossier/<int:id>/archive', methods=['POST'])
@login_required
@role_required('NOTAIRE')
def archive_dossier(id):
    from app.actes.services import ArchiveService
    
    try:
        result = ArchiveService.archive_dossier(id, current_user.id)
        flash(f'Dossier archivé avec succès. {result["archived_count"]} actes ajoutés au répertoire (N° {result["start_repertoire"]} à {result["end_repertoire"]}).', 'success')
    except ValueError as e:
        flash(str(e), 'warning')
    except Exception as e:
        flash(f'Erreur technique lors de l\'archivage: {str(e)}', 'error')
        print(f"ARCHIVE SERVICE ERROR: {e}")
        
    return redirect(url_for('dossiers.view', id=id))
