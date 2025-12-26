from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from app import db
from app.actes import bp
from app.actes.forms import TemplateForm, ActGenerationForm, TypeActeForm
from app.models import Template, Dossier, Acte, TypeActe
from jinja2 import Template as JinjaTemplate
from datetime import datetime
from io import BytesIO
import markdown2
import os
from werkzeug.utils import secure_filename
from docxtpl import DocxTemplate
from flask import send_file, make_response
import shutil
from pathlib import Path

from app.decorators import role_required

# --- TYPES D'ACTES ---

@bp.route('/types')
@login_required
@role_required('NOTAIRE', 'CLERC', 'ADMIN')
def types_acte_index():
    types = db.session.scalars(db.select(TypeActe).order_by(TypeActe.nom)).all()
    return render_template('actes/types_acte_index.html', types=types)

@bp.route('/types/new', methods=['GET', 'POST'])
@login_required
@role_required('NOTAIRE', 'ADMIN')
def type_acte_create():
    form = TypeActeForm()
    if form.validate_on_submit():
        ta = TypeActe(nom=form.nom.data, description=form.description.data)
        db.session.add(ta)
        db.session.commit()
        flash('Type d\'acte créé avec succès.', 'success')
        return redirect(url_for('actes.types_acte_index'))
    return render_template('actes/type_acte_form.html', form=form, title='Nouveau Type d\'Acte')

@bp.route('/types/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('NOTAIRE', 'ADMIN')
def type_acte_edit(id):
    ta = db.session.get(TypeActe, id)
    if not ta:
        flash('Type d\'acte introuvable.', 'error')
        return redirect(url_for('actes.types_acte_index'))
    form = TypeActeForm(obj=ta)
    if form.validate_on_submit():
        ta.nom = form.nom.data
        ta.description = form.description.data
        db.session.commit()
        flash('Type d\'acte mis à jour.', 'success')
        return redirect(url_for('actes.types_acte_index'))
    return render_template('actes/type_acte_form.html', form=form, title='Modifier Type d\'Acte')

@bp.route('/types/<int:id>/delete', methods=['POST'])
@login_required
@role_required('ADMIN')
def type_acte_delete(id):
    ta = db.session.get(TypeActe, id)
    if ta:
        if ta.templates or ta.actes:
            flash('Impossible de supprimer ce type car il est utilisé par des modèles ou des actes.', 'error')
        else:
            db.session.delete(ta)
            db.session.commit()
            flash('Type d\'acte supprimé.', 'success')
    return redirect(url_for('actes.types_acte_index'))

# --- MODELES ---
@bp.route('/templates')
@login_required
@role_required('NOTAIRE', 'CLERC', 'ADMIN')
def templates_index():
    templates = db.session.scalars(db.select(Template).order_by(Template.nom)).all()
    return render_template('actes/templates_index.html', templates=templates)

@bp.route('/templates/new', methods=['GET', 'POST'])
@login_required
@role_required('NOTAIRE', 'ADMIN')
def template_create():
    form = TemplateForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                filename = None
                is_docx = False
                if form.docx_file.data:
                    file = form.docx_file.data
                    filename = secure_filename(file.filename)
                    # Add timestamp to avoid collisions
                    filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
                    upload_folder = os.path.join(current_app.static_folder, 'templates_docx')
                    if not os.path.exists(upload_folder):
                        os.makedirs(upload_folder)
                    file.save(os.path.join(upload_folder, filename))
                    is_docx = True

                template = Template(
                    nom=form.nom.data,
                    type_acte_id=form.type_acte.data.id,
                    description=form.description.data,
                    contenu=form.contenu.data if not is_docx else None,
                    file_path=filename,
                    is_docx=is_docx
                )
                db.session.add(template)
                db.session.commit()
                flash('Modèle créé avec succès.', 'success')
                return redirect(url_for('actes.templates_index'))
            except Exception as e:
                db.session.rollback()
                flash(f'Erreur base de données lors de la création: {str(e)}', 'error')
                print(f"DATABASE ERROR in template_create: {str(e)}")
        else:
            # Log form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Erreur champ '{field}': {error}", 'error')
                    print(f"FORM ERROR in template_create: {field} - {error}")
                    
    return render_template('actes/template_form.html', form=form, title='Nouveau Modèle')

@bp.route('/templates/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('NOTAIRE', 'ADMIN')
def template_edit(id):
    template = db.session.get(Template, id)
    if not template:
        flash('Modèle introuvable.', 'error')
        return redirect(url_for('actes.templates_index'))
    
    form = TemplateForm(obj=template)
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                template.nom = form.nom.data
                template.type_acte_id = form.type_acte.data.id
                template.description = form.description.data
                template.contenu = form.contenu.data
                db.session.commit()
                flash('Modèle mis à jour.', 'success')
                return redirect(url_for('actes.templates_index'))
            except Exception as e:
                db.session.rollback()
                flash(f'Erreur base de données lors de la mise à jour: {str(e)}', 'error')
                print(f"DATABASE ERROR in template_edit: {str(e)}")
        else:
            # Log form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Erreur champ '{field}': {error}", 'error')
                    print(f"FORM ERROR in template_edit: {field} - {error}")

    return render_template('actes/template_form.html', form=form, title='Modifier Modèle', template=template)

@bp.route('/templates/<int:id>/delete', methods=['POST'])
@login_required
@role_required('NOTAIRE', 'ADMIN')
def template_delete(id):
    template = db.session.get(Template, id)
    if template:
        db.session.delete(template)
        db.session.commit()
        flash('Modèle supprimé.', 'success')
    return redirect(url_for('actes.templates_index'))

@bp.route('/generate', methods=['GET', 'POST'])
@login_required
@role_required('NOTAIRE', 'CLERC', 'ADMIN')
def generate():
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
            if template.is_docx:
                # DOCX Generation
                # Use static_folder for more robust path resolution in production
                template_path = os.path.join(current_app.static_folder, 'templates_docx', template.file_path)
                
                if not os.path.exists(template_path):
                    flash(f"Erreur : Le fichier modèle '{template.file_path}' est introuvable sur le serveur. Il a peut-être été supprimé lors d'un redémarrage. Veuillez le re-télécharger dans la gestion des modèles.", 'error')
                    return redirect(url_for('actes.generate'))
                
                try:
                    doc = DocxTemplate(template_path)
                    doc.render(context)
                except Exception as e:
                    flash(f"Erreur lors de la lecture du modèle Word : {str(e)}", 'error')
                    return redirect(url_for('actes.generate'))
                
                output = BytesIO()
                doc.save(output)
                output.seek(0)
                
                if form.save.data:
                    # Final Save
                    acte = Acte(
                        dossier_id=dossier.id,
                        type_acte=template.type_acte.nom,
                        type_acte_id=template.type_acte_id,
                        statut='BROUILLON',
                        version=1
                    )
                    db.session.add(acte)
                    db.session.commit()
                    
                    gen_filename = f"acte_{acte.id}.docx"
                    gen_folder = os.path.join(current_app.root_path, 'static', 'generated_actes')
                    if not os.path.exists(gen_folder):
                        os.makedirs(gen_folder)
                    
                    with open(os.path.join(gen_folder, gen_filename), 'wb') as f:
                        f.write(output.getvalue())
                    
                    flash('Acte Word généré et sauvegardé avec succès.', 'success')
                    return redirect(url_for('actes.view_act', id=acte.id))
                else:
                    # Temporary Preview
                    temp_folder = os.path.join(current_app.root_path, 'static', 'temp_previews')
                    if not os.path.exists(temp_folder):
                        os.makedirs(temp_folder)
                    
                    # Cleanup old temp files (older than 1 hour)
                    import time
                    try:
                        now_ts = time.time()
                        for f in os.listdir(temp_folder):
                            f_path = os.path.join(temp_folder, f)
                            if os.path.isfile(f_path) and os.stat(f_path).st_mtime < now_ts - 3600:
                                os.remove(f_path)
                    except Exception as cleanup_err:
                        print(f"Temp Cleanup error: {cleanup_err}")
                    
                    temp_filename = f"preview_{current_user.id}_{datetime.utcnow().strftime('%H%M%S')}.docx"
                    temp_path = os.path.join(temp_folder, temp_filename)
                    with open(temp_path, 'wb') as f:
                        f.write(output.getvalue())
                    
                    preview_docx_url = url_for('static', filename=f'temp_previews/{temp_filename}')
                    flash('Génération Word réussie (Prévisualisation).', 'success')
                    return render_template('actes/generate.html', form=form, preview_docx_url=preview_docx_url, title='Générer un Acte')

            else:
                # Legacy Markdown Generation
                jinja_template = JinjaTemplate(template.contenu)
                rendered_markdown = jinja_template.render(context)
                preview_content = markdown2.markdown(rendered_markdown, extras=["tables", "fenced-code-blocks"])
                
                if form.save.data:
                    acte = Acte(
                        dossier_id=dossier.id,
                        type_acte=template.type_acte.nom,
                        type_acte_id=template.type_acte_id,
                        contenu_html=preview_content,
                        statut='BROUILLON',
                        version=1
                    )
                    db.session.add(acte)
                    db.session.commit()
                    flash('Acte sauvegardé avec succès.', 'success')
                    return redirect(url_for('actes.view_act', id=acte.id))
                
                flash('Génération réussie (Prévisualisation).', 'success')
        except Exception as e:
            flash(f'Erreur lors de la génération: {str(e)}', 'error')
            print(f"GENERATION ERROR: {str(e)}")

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
    html_content = f"""
    <html>
    <head>
        <style>
            @page {{ size: a4; margin: 2cm; }}
            body {{ font-family: Helvetica, Arial, sans-serif; font-size: 12pt; }}
        </style>
    </head>
    <body>
        {acte.contenu_html}
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
            acte.contenu_html = form.contenu_html.data
            flash('Contenu mis à jour.', 'success')
        
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
    
    # Placeholder for electronic signature logic
    # In a real app, this would involve a certificate and a hash
    acte.statut = 'SIGNE'
    acte.date_signature = datetime.utcnow()
    acte.signature_electronique = f"SIGNED-BY-{current_user.username}-{datetime.utcnow().isoformat()}"
    db.session.commit()
    
    flash('L\'acte a été signé électroniquement.', 'success')
    return redirect(url_for('actes.view_act', id=id))

# --- ARCHIVAGE ET RÉPERTOIRE ---

@bp.route('/repertoire')
@login_required
@role_required('NOTAIRE', 'CLERC', 'ADMIN')
def repertoire_index():
    # Formal Notarial Index: Only archived acts
    archived_acts = db.session.scalars(
        db.select(Acte).filter(Acte.numero_repertoire != None).order_by(Acte.numero_repertoire.desc())
    ).all()
    return render_template('actes/repertoire.html', acts=archived_acts)

@bp.route('/dossier/<int:id>/archive', methods=['POST'])
@login_required
@role_required('NOTAIRE')
def archive_dossier(id):
    dossier = db.session.get(Dossier, id)
    if not dossier or dossier.statut == 'ARCHIVE':
        flash('Dossier introuvable ou déjà archivé.', 'error')
        return redirect(url_for('dossiers.index'))
    
    # Selective Archiving: Filter for SIGNE acts
    signed_acts = [a for a in dossier.actes if a.statut == 'SIGNE']
    
    if not signed_acts:
        flash('Aucun acte signé à archiver dans ce dossier.', 'warning')
        return redirect(url_for('dossiers.view', id=id))

    try:
        # Create archive folder
        archive_root = Path(current_app.static_folder) / 'archives'
        dossier_archive_path = archive_root / str(dossier.id)
        dossier_archive_path.mkdir(parents=True, exist_ok=True)
        
        # Get next Repertoire number for this year
        year = datetime.utcnow().year
        max_rep = db.session.scalar(
            db.select(db.func.max(Acte.numero_repertoire)).filter(
                db.extract('year', Acte.date_archivage) == year
            )
        ) or 0
        
        # Archive signed acts
        for acte in signed_acts:
            filename = f"acte_{acte.id}.docx"
            src_path = Path(current_app.static_folder) / 'generated_actes' / filename
            
            if src_path.exists():
                # Move to archive vault
                dest_path = dossier_archive_path / filename
                shutil.move(str(src_path), str(dest_path))
                
                # Update Acte Metadata
                max_rep += 1
                acte.numero_repertoire = max_rep
                acte.date_archivage = datetime.utcnow()
                acte.archive_par_id = current_user.id
                acte.statut = 'ARCHIVE'
        
        # Archive Accounting (Receipts / Invoices)
        # We also move their PDFs if they exist
        # Implementation note: For simplicity in this phase, we just mark the dossier as ARCHIVE
        # and lock the files.
        
        dossier.statut = 'ARCHIVE'
        db.session.commit()
        
        flash(f'Dossier archivé avec succès. {len(signed_acts)} actes ajoutés au répertoire.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de l\'archivage: {str(e)}', 'error')
        print(f"ARCHIVE ERROR: {e}")
        
    return redirect(url_for('dossiers.view', id=id))
