from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required
from app import db
from app.actes import bp
from app.actes.forms import TemplateForm, ActGenerationForm, TypeActeForm
from app.models import Template, Dossier, Acte, TypeActe
from jinja2 import Template as JinjaTemplate
from datetime import datetime
from io import BytesIO
import markdown2
from flask import send_file, make_response

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
    if form.validate_on_submit():
        template = Template(
            nom=form.nom.data,
            type_acte_id=form.type_acte.data.id,
            description=form.description.data,
            contenu=form.contenu.data
        )
        db.session.add(template)
        db.session.commit()
        flash('Modèle créé avec succès.', 'success')
        return redirect(url_for('actes.templates_index'))
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
    if form.validate_on_submit():
        template.nom = form.nom.data
        template.type_acte_id = form.type_acte.data.id
        template.description = form.description.data
        template.contenu = form.contenu.data
        db.session.commit()
        flash('Modèle mis à jour.', 'success')
        return redirect(url_for('actes.templates_index'))
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
            'client': dossier.parties[0].client if dossier.parties else None, # Simplification: take first client
            'vendeur': next((p.client for p in dossier.parties if p.role_dans_acte.lower() == 'vendeur'), None),
            'acheteur': next((p.client for p in dossier.parties if p.role_dans_acte.lower() == 'acheteur'), None),
            'date': datetime.utcnow().strftime('%d/%m/%Y'),
            'now': datetime.utcnow(),
            'current_user': current_user,
        }
        
        try:
            jinja_template = JinjaTemplate(template.contenu)
            rendered_markdown = jinja_template.render(context)
            preview_content = markdown2.markdown(rendered_markdown, extras=["tables", "fenced-code-blocks"])
            
            if form.save.data:
                # Save the act
                acte = Acte(
                    dossier_id=dossier.id,
                    type_acte=template.type_acte.nom,
                    type_acte_id=template.type_acte_id,
                    contenu_html=preview_content,
                    statut='BROUILLON',
                    version=1,
                    date_signature=None # A init null
                )
                db.session.add(acte)
                db.session.commit()
                flash('Acte sauvegardé avec succès.', 'success')
                return redirect(url_for('actes.view_act', id=acte.id))
            
            flash('Génération réussie (Prévisualisation).', 'success')
        except Exception as e:
            flash(f'Erreur lors de la génération: {str(e)}', 'error')

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
def download_pdf(id):
    acte = db.session.get(Acte, id)
    if not acte:
        flash('Acte non trouvé.', 'error')
        return redirect(url_for('dossiers.index'))

    # Create PDF using xhtml2pdf
    from xhtml2pdf import pisa
    
    # Simple HTML wrapper for PDF
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
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"acte_{acte.id}.pdf",
        mimetype='application/pdf'
    )
