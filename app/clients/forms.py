from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, Length

class ClientForm(FlaskForm):
    type_client = SelectField('Type de Client', choices=[('PHYSIQUE', 'Personne Physique'), ('MORALE', 'Personne Morale')], validators=[DataRequired()])
    nom = StringField('Nom', validators=[DataRequired(), Length(max=100)])
    prenom = StringField('Prénom', validators=[Optional(), Length(max=100)])
    date_naissance = DateField('Date de Naissance', format='%Y-%m-%d', validators=[Optional()])
    lieu_naissance = StringField('Lieu de Naissance', validators=[Optional(), Length(max=100)])
    adresse = TextAreaField('Adresse', validators=[Optional()])
    telephone = StringField('Téléphone', validators=[Optional(), Length(max=30)])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=100)])
    identifiant_unique = StringField('Identifiant Unique (CNI/NINEA)', validators=[Optional(), Length(max=50)])
    submit = SubmitField('Enregistrer')
