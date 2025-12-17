from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, SelectField
from wtforms.validators import DataRequired
from wtforms_sqlalchemy.fields import QuerySelectField
from app import db
from app.models import Dossier, Template

class TemplateForm(FlaskForm):
    nom = StringField('Nom du Modèle', validators=[DataRequired()])
    type_acte = SelectField('Type d\'Acte', choices=[
        ('VENTE', 'Vente Immobilière'),
        ('PROCURATION', 'Procuration'),
        ('CONTRAT', 'Contrat Divers'),
        ('TESTAMENT', 'Testament'),
        ('DIVERS', 'Autre')
    ])
    description = TextAreaField('Description')
    contenu = TextAreaField('Contenu (HTML/Jinja2)', validators=[DataRequired()], render_kw={"rows": 20})
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
