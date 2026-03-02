from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required
from app import db
from app.actes import bp
from app.actes.forms import TemplateForm, TypeActeForm
from app.models import Template, TypeActe
from app.decorators import role_required
import os
from werkzeug.utils import secure_filename
from datetime import datetime

# --- TYPES D'ACTES ---

@bp.route('/types')
@login_required
@role_required('NOTAIRE', 'CLERC', 'ADMIN')
def types_acte_index():
    dossier_id = request.args.get('dossier_id')
    types = db.session.scalars(db.select(TypeActe).order_by(TypeActe.nom)).all()
    return render_template('actes/types_acte_index.html', types=types, dossier_id=dossier_id)

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
                    # Validate extension (SEC-10)
                    if not filename.lower().endswith('.docx'):
                        flash('Seuls les fichiers .docx sont autorisés.', 'error')
                        return render_template('actes/template_form.html', form=form, title='Nouveau Modèle')
                    
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
                current_app.logger.error(f"DATABASE ERROR in template_create: {str(e)}")
                flash('Une erreur est survenue lors de la création du modèle.', 'error')
        else:
            # Log form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    current_app.logger.warning(f"FORM ERROR in template_create: {field} - {error}")
                    flash(f"Erreur champ '{field}': {error}", 'error')
                    
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
                current_app.logger.error(f"DATABASE ERROR in template_edit: {str(e)}")
                flash('Une erreur est survenue lors de la mise à jour du modèle.', 'error')
        else:
            # Log form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    current_app.logger.warning(f"FORM ERROR in template_edit: {field} - {error}")
                    flash(f"Erreur champ '{field}': {error}", 'error')

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
