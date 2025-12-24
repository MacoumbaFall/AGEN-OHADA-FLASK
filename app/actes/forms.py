from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional
from wtforms_sqlalchemy.fields import QuerySelectField
from app import db
from app.models import Dossier, Template, TypeActe

def enabled_type_actes():
    return db.session.execute(db.select(TypeActe).order_by(TypeActe.nom)).scalars()

class ActEditForm(FlaskForm):
    contenu_html = TextAreaField('Contenu (Markdown)', validators=[Optional()])
    docx_file = FileField('Remplacer le fichier Word (.docx)', validators=[FileAllowed(['docx'], 'Fichiers Word uniquement.')])
    submit = SubmitField('Enregistrer les modifications')

class TypeActeForm(FlaskForm):
    nom = StringField('Nom du Type d\'Acte', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Enregistrer')

class TemplateForm(FlaskForm):
    nom = StringField('Nom du Modèle', validators=[DataRequired()])
    type_acte = QuerySelectField('Type d\'Acte', query_factory=enabled_type_actes, get_label='nom', allow_blank=False)
    description = TextAreaField('Description')
    contenu = TextAreaField('Contenu (Markdown & Jinja2)', validators=[Optional()], render_kw={"rows": 10})
    docx_file = FileField('Fichier Word (.docx)', validators=[
        FileAllowed(['docx'], 'Seuls les fichiers .docx sont autorisés.')
    ])
    submit = SubmitField('Enregistrer')

def enabled_dossiers():
    return db.session.execute(db.select(Dossier).order_by(Dossier.numero_dossier)).scalars()

def enabled_templates():
    return db.session.execute(db.select(Template).order_by(Template.nom)).scalars()

class ActGenerationForm(FlaskForm):
    dossier = QuerySelectField('Dossier', query_factory=enabled_dossiers, get_label='numero_dossier', allow_blank=False)
    template = QuerySelectField('Modèle', query_factory=enabled_templates, get_label='nom', allow_blank=False)
    submit = SubmitField('Prévisualiser l\'Acte')
    save = SubmitField('Valider et Sauvegarder')
