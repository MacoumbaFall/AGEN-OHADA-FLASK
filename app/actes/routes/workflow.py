from flask import render_template, flash, redirect, url_for, request, current_app, send_file
from flask_login import login_required, current_user
from app import db
from app.actes import bp
from app.actes.forms import ActGenerationForm
from app.models import Dossier, Acte, Template
from app.decorators import role_required
from datetime import datetime
from io import BytesIO
import markdown2
import os
from werkzeug.utils import secure_filename
from docxtpl import DocxTemplate
from jinja2.sandbox import SandboxedEnvironment
import bleach

@bp.route('/generate', methods=['GET', 'POST'])
@login_required
@role_required('NOTAIRE', 'CLERC', 'ADMIN')
def generate():
    from app.actes.services import ActGeneratorService
    
    form = ActGenerationForm()
    preview_content = None
    
    if form.validate_on_submit():
        dossier = form.dossier.data
        template = form.template.data
        
        # Context for Jinja2 substitution
        context = {
            'dossier': dossier,
            'template': template,
            'client': dossier.parties[0].client if dossier.parties else None,
            'vendeur': next((p.client for p in dossier.parties if p.role_dans_acte.lower() == 'vendeur'), None),
            'acheteur': next((p.client for p in dossier.parties if p.role_dans_acte.lower() == 'acheteur'), None),
            'date': datetime.utcnow().strftime('%d/%m/%Y'),
            'now': datetime.utcnow(),
            'current_user': current_user,
        }
        
        try:
            result = ActGeneratorService.generate_act(
                dossier=dossier,
                template=template,
                context=context,
                save_mode=form.save.data,
                user=current_user
            )
            
            if result['type'] == 'docx':
                if form.save.data:
                    flash('Acte Word généré et sauvegardé avec succès.', 'success')
                    return redirect(result['download_url'])
                else:
                    flash('Génération Word réussie (Prévisualisation).', 'success')
                    return render_template('actes/generate.html', form=form, preview_docx_url=result['preview_url'], title='Générer un Acte')
            
            elif result['type'] == 'html':
                preview_content = result['content']
                if form.save.data:
                    flash('Acte sauvegardé avec succès.', 'success')
                    return redirect(url_for('actes.view_act', id=result['acte_id']))
                else:
                    flash('Génération réussie (Prévisualisation).', 'success')

        except Exception as e:
            current_app.logger.error(f"GENERATION ERROR: {str(e)}")
            flash(f'Une erreur est survenue lors de la génération de l\'acte.', 'error')

    return render_template('actes/generate.html', form=form, preview_content=preview_content, title='Générer un Acte')

@bp.route('/view/<int:id>')
@login_required
@role_required('NOTAIRE', 'CLERC', 'ADMIN')
def view_act(id):
    acte = db.session.get(Acte, id)
    if not acte:
        flash('Acte non trouvé.', 'error')
        return redirect(url_for('dossiers.index'))
    
    return render_template('actes/view.html', acte=acte)

@bp.route('/download/<int:id>')
@login_required
@role_required('NOTAIRE', 'CLERC', 'ADMIN')
def download_docx(id):
    acte = db.session.get(Acte, id)
    if not acte or not acte.dossier:
        flash('Acte ou dossier non trouvé.', 'error')
        return redirect(url_for('dossiers.index'))

    filename = f"acte_{acte.id}.docx"
    filepath = os.path.join(current_app.static_folder, 'generated_actes', filename)
    
    # If not found in generated_actes, check archives
    if not os.path.exists(filepath):
        filepath = os.path.join(current_app.static_folder, 'archives', str(acte.dossier_id), filename)
    
    if not os.path.exists(filepath):
        flash('Fichier Word introuvable.', 'error')
        return redirect(url_for('actes.view_act', id=id))
        
    return send_file(
        filepath,
        as_attachment=True,
        download_name=f"acte_{acte.id}.docx",
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )

@bp.route('/signature_page/<int:id>')
@login_required
@role_required('NOTAIRE', 'CLERC', 'ADMIN')
def signature_page(id):
    from app.actes.services.parametres import ParametreService
    acte = db.session.get(Acte, id)
    if not acte:
        flash('Acte non trouvé.', 'error')
        return redirect(url_for('dossiers.index'))
    return render_template('actes/signature_page.html', acte=acte, p=ParametreService)

@bp.route('/download_pdf/<int:id>')
@login_required
@role_required('NOTAIRE', 'CLERC', 'ADMIN')
def download_pdf(id):
    acte = db.session.get(Acte, id)
    if not acte:
        flash('Acte non trouvé.', 'error')
        return redirect(url_for('dossiers.index'))

    if not acte.contenu_html:
        flash('La conversion PDF pour les fichiers Word n\'est pas encore disponible. Téléchargez le Word.', 'warning')
        return redirect(url_for('actes.view_act', id=id))

    # Existing PDF generation for HTML/Markdown
    from xhtml2pdf import pisa
    # Sanitize HTML before PDF generation (SEC-04)
    allowed_tags = bleach.ALLOWED_TAGS | {
        'p', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 
        'span', 'div', 'hr', 'strong', 'em', 'u', 's', 'cite', 'code', 'pre', 'b', 'i'
    }
    allowed_attrs = {**bleach.ALLOWED_ATTRIBUTES, 'style': ['text-align', 'margin-left', 'width', 'font-family', 'font-size']}
    sanitized_html = bleach.clean(acte.contenu_html, tags=allowed_tags, attributes=allowed_attrs)

    html_content = f"""
    <html>
    <head>
        <style>
            @page {{ size: a4; margin: 2cm; }}
            body {{ font-family: Helvetica, Arial, sans-serif; font-size: 12pt; }}
        </style>
    </head>
    <body>
        {sanitized_html}
    </body>
    </html>
    """
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)
    if pisa_status.err:
        flash('Erreur lors de la génération du PDF.', 'error')
        return redirect(url_for('actes.view_act', id=id))
    pdf_buffer.seek(0)
    return send_file(pdf_buffer, as_attachment=True, download_name=f"acte_{acte.id}.pdf", mimetype='application/pdf')

# --- FINALISATION ET RÉVISION ---

@bp.route('/review')
@login_required
@role_required('NOTAIRE')
def review_dashboard():
    # Only drafts for notaries
    drafts = db.session.scalars(
        db.select(Acte).filter_by(statut='BROUILLON').order_by(Acte.created_at.desc())
    ).all()
    return render_template('actes/review.html', acts=drafts)

@bp.route('/<int:id>/edit_draft', methods=['GET', 'POST'])
@login_required
@role_required('NOTAIRE')
def edit_draft(id):
    acte = db.session.get(Acte, id)
    if not acte or acte.statut != 'BROUILLON':
        flash('Acte introuvable ou déjà finalisé.', 'error')
        return redirect(url_for('actes.review_dashboard'))
    
    from app.actes.forms import ActEditForm
    form = ActEditForm(obj=acte)
    
    if form.validate_on_submit():
        if acte.contenu_html and form.contenu_html.data:
            # Sanitize HTML from manual edit (SEC-01)
            allowed_tags = bleach.ALLOWED_TAGS | {
                'p', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 
                'span', 'div', 'hr', 'strong', 'em', 'u', 's', 'cite', 'code', 'pre', 'b', 'i'
            }
            allowed_attrs = {**bleach.ALLOWED_ATTRIBUTES, 'style': ['text-align', 'margin-left', 'width', 'font-family', 'font-size']}
            acte.contenu_html = bleach.clean(form.contenu_html.data, tags=allowed_tags, attributes=allowed_attrs)
            flash('Contenu mis à jour (et sécurisé).', 'success')
        
        if form.docx_file.data:
            file = form.docx_file.data
            filename = f"acte_{acte.id}.docx" # Keep same filename for the act
            upload_folder = os.path.join(current_app.root_path, 'static', 'generated_actes')
            file.save(os.path.join(upload_folder, filename))
            flash('Fichier Word remplacé avec succès.', 'success')
            
        db.session.commit()
        return redirect(url_for('actes.view_act', id=acte.id))
        
    return render_template('actes/edit_draft.html', form=form, acte=acte)

@bp.route('/<int:id>/finalize', methods=['POST'])
@login_required
@role_required('NOTAIRE')
def finalize_act(id):
    acte = db.session.get(Acte, id)
    if not acte or acte.statut != 'BROUILLON':
        flash('Action impossible.', 'error')
        return redirect(url_for('actes.view_act', id=id))
    
    acte.statut = 'FINALISE'
    acte.finalise_par_id = current_user.id
    acte.date_finalisation = datetime.utcnow()
    db.session.commit()
    
    flash('L\'acte a été finalisé et verrouillé.', 'success')
    return redirect(url_for('actes.view_act', id=id))

@bp.route('/<int:id>/sign', methods=['POST'])
@login_required
@role_required('NOTAIRE')
def sign_act(id):
    acte = db.session.get(Acte, id)
    if not acte or acte.statut != 'FINALISE':
        flash('Seul un acte finalisé peut être signé.', 'error')
        return redirect(url_for('actes.view_act', id=id))
    
    # Improved placeholder for electronic signature logic (SEC-12)
    # We add a hash of the content to provide some integrity verification
    import hashlib
    content_to_hash = (acte.contenu_html or "").encode()
    content_hash = hashlib.sha256(content_to_hash).hexdigest()
    
    acte.statut = 'SIGNE'
    acte.date_signature = datetime.utcnow()
    acte.signature_electronique = f"SIGNED-BY-{current_user.username}-{datetime.utcnow().isoformat()}-HASH-{content_hash[:16]}"
    db.session.commit()
    
    flash('L\'acte a été signé électroniquement.', 'success')
    return redirect(url_for('actes.view_act', id=id))
