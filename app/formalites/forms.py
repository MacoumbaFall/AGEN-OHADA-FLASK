from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Optional
from wtforms_sqlalchemy.fields import QuerySelectField
from app import db
from app.models import Dossier

def enabled_dossiers():
    return db.session.execute(db.select(Dossier).order_by(Dossier.numero_dossier)).scalars()

class FormaliteForm(FlaskForm):
    dossier = QuerySelectField('Dossier', query_factory=enabled_dossiers, get_label='numero_dossier', allow_blank=False)
    type_formalite = SelectField('Type de Formalité', choices=[
        ('ENREGISTREMENT', 'Enregistrement Impôts'),
        ('HYPOTHEQUE', 'Inscription Hypothécaire'),
        ('RCCM', 'Dépôt RCCM'),
        ('JOURNAL', 'Publication Journal Officiel'),
        ('CADASTRE', 'Formalités Cadastrales'),
        ('DIVERS', 'Autre')
    ], validators=[DataRequired()])
    statut = SelectField('Statut', choices=[
        ('A_FAIRE', 'À Faire'),
        ('EN_COURS', 'En Cours'),
        ('DEPOSE', 'Déposé'),
        ('TERMINE', 'Terminé'),
        ('ANNULE', 'Annulé')
    ], default='A_FAIRE')
    date_depot = DateField('Date de Dépôt', validators=[Optional()])
    date_retour = DateField('Date de Retour Prévue/Réelle', validators=[Optional()])
    cout_estime = DecimalField('Coût Estimé', places=2, validators=[Optional()])
    cout_reel = DecimalField('Coût Réel', places=2, validators=[Optional()])
    reference_externe = StringField('Référence Externe (Quittance, Numéro...)')
    submit = SubmitField('Enregistrer')
