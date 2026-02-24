from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, SubmitField, DecimalField
from wtforms.validators import DataRequired, Email, Optional, Length

class ClientForm(FlaskForm):
    type_client = SelectField('Type de Client', choices=[('PHYSIQUE', 'Personne Physique'), ('MORALE', 'Personne Morale')], validators=[DataRequired()])
    nom = StringField('Nom / Raison Sociale', validators=[DataRequired(), Length(max=100)])
    prenom = StringField('Prénom (Optionnel pour PM)', validators=[Optional(), Length(max=100)])
    date_naissance = DateField('Date de Naissance / Création', format='%Y-%m-%d', validators=[Optional()])
    lieu_naissance = StringField('Lieu de Naissance / Création', validators=[Optional(), Length(max=100)])
    
    # --- Personne Physique ---
    profession = StringField('Profession', validators=[Optional(), Length(max=100)])
    nationalite = StringField('Nationalité', validators=[Optional(), Length(max=50)])
    situation_matrimoniale = SelectField('Situation Matrimoniale', choices=[('', '---'), ('CÉLIBATAIRE', 'Célibataire'), ('MARIÉ(E)', 'Marié(e)'), ('DIVORCÉ(E)', 'Divorcé(e)'), ('VEUF/VEUVE', 'Veuf/Veuve')], validators=[Optional()])
    regime_matrimonial = StringField('Régime Matrimonial', validators=[Optional(), Length(max=100)])
    
    # --- Personne Morale ---
    forme_juridique = StringField('Forme Juridique', validators=[Optional(), Length(max=50)])
    capital_social = DecimalField('Capital Social', validators=[Optional()])
    rccm = StringField('Numéro RCCM', validators=[Optional(), Length(max=100)])
    ninea = StringField('NINEA', validators=[Optional(), Length(max=100)])
    
    # --- Coordonnées ---
    adresse = TextAreaField('Adresse Principale', validators=[Optional()])
    telephone = StringField('Téléphone', validators=[Optional(), Length(max=30)])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=100)])
    identifiant_unique = StringField('Identifiant Unique Ancien (Optionnel)', validators=[Optional(), Length(max=50)])
    
    # --- KYC / Pièces d'identité ---
    type_piece_identite = SelectField('Type de Pièce', choices=[('', '---'), ('CNI', 'Carte Nationale d\'Identité'), ('PASSEPORT', 'Passeport'), ('CARTE_CONSULAIRE', 'Carte Consulaire'), ('EXTRAIT_RCCM', 'Extrait RCCM'), ('AUTRE', 'Autre')], validators=[Optional()])
    numero_piece_identite = StringField('Numéro de Pièce', validators=[Optional(), Length(max=100)])
    date_emission_piece = DateField('Date d\'émission de la pièce', format='%Y-%m-%d', validators=[Optional()])
    date_expiration_piece = DateField('Date d\'expiration de la pièce', format='%Y-%m-%d', validators=[Optional()])
    autorite_emission_piece = StringField('Autorité d\'émission', validators=[Optional(), Length(max=100)])
    
    # --- Statut KYC ---
    kyc_statut = SelectField('Statut KYC', choices=[('A_VERIFIER', 'À vérifier'), ('VALIDE', 'Valide'), ('EXPIRE', 'Expiré'), ('REJETE', 'Rejeté')], default='A_VERIFIER', validators=[DataRequired()])
    kyc_notes = TextAreaField('Notes KYC', validators=[Optional()])

    submit = SubmitField('Enregistrer le Client')

