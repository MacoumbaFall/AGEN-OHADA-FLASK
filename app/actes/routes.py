from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required
from app import db
from app.actes import bp
from app.actes.forms import TemplateForm, ActGenerationForm
from app.models import Template, Dossier, Acte
from jinja2 import Template as JinjaTemplate
from datetime import datetime
from xhtml2pdf import pisa
from io import BytesIO
from flask import send_file, make_response

@bp.route('/templates')
@login_required
def templates_index():
    templates = db.session.scalars(db.select(Template).order_by(Template.nom)).all()
    return render_template('actes/templates_index.html', templates=templates)

@bp.route('/templates/new', methods=['GET', 'POST'])
@login_required
def template_create():
    form = TemplateForm()
    if form.validate_on_submit():
        template = Template(
            nom=form.nom.data,
            type_acte=form.type_acte.data,
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
def template_edit(id):
    template = db.session.get(Template, id)
    if not template:
        flash('Modèle introuvable.', 'error')
        return redirect(url_for('actes.templates_index'))
    
    form = TemplateForm(obj=template)
    if form.validate_on_submit():
        template.nom = form.nom.data
        template.type_acte = form.type_acte.data
        template.description = form.description.data
        template.contenu = form.contenu.data
        db.session.commit()
        flash('Modèle mis à jour.', 'success')
        return redirect(url_for('actes.templates_index'))
    return render_template('actes/template_form.html', form=form, title='Modifier Modèle', template=template)

@bp.route('/templates/<int:id>/delete', methods=['POST'])
@login_required
def template_delete(id):
    template = db.session.get(Template, id)
    if template:
        db.session.delete(template)
        db.session.commit()
        flash('Modèle supprimé.', 'success')
    return redirect(url_for('actes.templates_index'))

@bp.route('/generate', methods=['GET', 'POST'])
@login_required
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
        }
        
        try:
            jinja_template = JinjaTemplate(template.contenu)
            preview_content = jinja_template.render(context)
            
            if form.save.data:
                # Save the act
                acte = Acte(
                    dossier_id=dossier.id,
                    type_acte=template.type_acte,
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
def view_act(id):
    acte = db.session.get(Acte, id)
    if not acte:
        flash('Acte non trouvé.', 'error')
        return redirect(url_for('dossiers.index'))
    return render_template('actes/view.html', acte=acte)

@bp.route('/download/<int:id>')
@login_required
def download_pdf(id):
    acte = db.session.get(Acte, id)
    if not acte:
        flash('Acte non trouvé.', 'error')
        return redirect(url_for('dossiers.index'))

    # Create PDF
    pdf_buffer = BytesIO()
    
    # Simple HTML wrapper for PDF
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: sans-serif; font-size: 12pt; }}
            @page {{ size: A4; margin: 2cm; }}
        </style>
    </head>
    <body>
        {acte.contenu_html}
    </body>
    </html>
    """
    
    pisa_status = pisa.CreatePDF(src=html_content, dest=pdf_buffer)
    
    if pisa_status.err:
        flash('Erreur lors de la création du PDF.', 'error')
        return redirect(url_for('actes.view_act', id=id))
        
    pdf_buffer.seek(0)
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"acte_{acte.id}.pdf",
        mimetype='application/pdf'
    )
