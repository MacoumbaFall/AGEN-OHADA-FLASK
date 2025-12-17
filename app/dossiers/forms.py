from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional, Length

class DossierForm(FlaskForm):
    numero_dossier = StringField('Numéro Dossier', validators=[DataRequired(), Length(min=2, max=50)])
    intitule = StringField('Intitulé', validators=[DataRequired(), Length(max=200)])
    type_dossier = SelectField('Type de Dossier', choices=[
        ('VENTE', 'Vente Immobilière'),
        ('SUCCESSION', 'Succession'),
        ('SOCIETE', 'Constitution de Société'),
        ('PRET', 'Prêt Hypothécaire'),
        ('DIVERS', 'Divers')
    ])
    statut = SelectField('Statut', choices=[
        ('OUVERT', 'Ouvert'),
        ('EN_COURS', 'En cours'),
        ('ATTENTE', 'En attente'),
        ('CLOS', 'Clôturé'),
        ('ARCHIVE', 'Archivé')
    ], default='OUVERT')
    date_ouverture = DateField('Date d\'Ouverture', format='%Y-%m-%d', validators=[Optional()])
    responsable_id = SelectField('Responsable', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Enregistrer')

class DossierPartyForm(FlaskForm):
    client_id = SelectField('Client', coerce=int, validators=[DataRequired()])
    role_dans_acte = StringField('Rôle dans l\'acte', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Ajouter la partie')
