from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, DecimalField, TextAreaField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Optional, NumberRange
from wtforms_sqlalchemy.fields import QuerySelectField
from app import db
from app.models import Dossier, Client, ComptaCompte

def enabled_dossiers():
    return db.session.execute(db.select(Dossier).order_by(Dossier.numero_dossier)).scalars()

def enabled_clients():
    return db.session.execute(db.select(Client).order_by(Client.nom)).scalars()

def active_comptes():
    return db.session.execute(db.select(ComptaCompte).filter_by(actif=True).order_by(ComptaCompte.numero_compte)).scalars()

def office_comptes():
    return db.session.execute(db.select(ComptaCompte).filter_by(actif=True, categorie='OFFICE').order_by(ComptaCompte.numero_compte)).scalars()

def client_comptes():
    return db.session.execute(db.select(ComptaCompte).filter_by(actif=True, categorie='CLIENT').order_by(ComptaCompte.numero_compte)).scalars()

class CompteForm(FlaskForm):
    """Form for creating/editing accounts."""
    numero_compte = StringField('Numéro de Compte', validators=[DataRequired()])
    libelle = StringField('Libellé', validators=[DataRequired()])
    type_compte = SelectField('Type de Compte', choices=[
        ('GENERAL', 'Compte Général'),
        ('CLIENT', 'Compte Client'),
        ('TIERS', 'Compte Tiers')
    ], validators=[DataRequired()])
    categorie = SelectField('Catégorie', choices=[
        ('', '-- Sélectionner --'),
        ('OFFICE', 'Compte Office'),
        ('CLIENT', 'Compte Client (Fonds de tiers)')
    ])
    actif = SelectField('Statut', choices=[
        ('True', 'Actif'),
        ('False', 'Inactif')
    ], default='True')
    submit_btn = SubmitField('Enregistrer')

class EcritureForm(FlaskForm):
    """Form for creating accounting entries."""
    date_ecriture = DateField('Date', validators=[DataRequired()])
    numero_piece = StringField('N° Pièce')
    libelle_operation = StringField('Libellé', validators=[DataRequired()])
    journal_code = SelectField('Journal', choices=[
        ('BQ', 'Banque'),
        ('CA', 'Caisse'),
        ('OD', 'Opérations Diverses'),
        ('VT', 'Ventes')
    ], validators=[DataRequired()])
    dossier = QuerySelectField('Dossier (optionnel)', query_factory=enabled_dossiers, 
                               get_label='numero_dossier', allow_blank=True, blank_text='-- Aucun --')
    submit_btn = SubmitField('Enregistrer')

class RecuForm(FlaskForm):
    """Form for creating receipts."""
    date_emission = DateField('Date d\'émission', validators=[DataRequired()])
    dossier = QuerySelectField('Dossier', query_factory=enabled_dossiers, 
                               get_label='numero_dossier', allow_blank=True, blank_text='-- Sélectionner --')
    client = QuerySelectField('Client', query_factory=enabled_clients,
                             get_label=lambda c: f"{c.nom} {c.prenom or ''}".strip(),
                             allow_blank=True, blank_text='-- Sélectionner --')
    montant = DecimalField('Montant (FCFA)', validators=[DataRequired(), NumberRange(min=0)], places=2)
    mode_paiement = SelectField('Mode de Paiement', choices=[
        ('ESPECES', 'Espèces'),
        ('CHEQUE', 'Chèque'),
        ('VIREMENT', 'Virement Bancaire'),
        ('MOBILE', 'Mobile Money')
    ], validators=[DataRequired()])
    reference_paiement = StringField('Référence (N° Chèque, N° Transaction...)')
    motif = TextAreaField('Motif', validators=[DataRequired()])
    submit_btn = SubmitField('Émettre le Reçu')

class FactureForm(FlaskForm):
    """Form for creating invoices."""
    date_emission = DateField('Date d\'émission', validators=[DataRequired()])
    date_echeance = DateField('Date d\'échéance')
    dossier = QuerySelectField('Dossier', query_factory=enabled_dossiers,
                               get_label='numero_dossier', allow_blank=True, blank_text='-- Sélectionner --')
    client = QuerySelectField('Client', query_factory=enabled_clients,
                             get_label=lambda c: f"{c.nom} {c.prenom or ''}".strip(),
                             allow_blank=True, blank_text='-- Sélectionner --')
    montant_ht = DecimalField('Montant HT (FCFA)', validators=[DataRequired(), NumberRange(min=0)], places=2)
    montant_tva = DecimalField('TVA (FCFA)', validators=[Optional(), NumberRange(min=0)], places=2, default=0)
    description = TextAreaField('Description', validators=[DataRequired()])
    submit_btn = SubmitField('Créer la Facture')

class RecetteForm(FlaskForm):
    """Simplified form for recording income."""
    date_operation = DateField('Date', validators=[DataRequired()])
    libelle = StringField('Libellé', validators=[DataRequired()])
    montant = DecimalField('Montant (FCFA)', validators=[DataRequired(), NumberRange(min=0)], places=2)
    mode_paiement = SelectField('Mode de Paiement', choices=[
        ('ESPECES', 'Espèces'),
        ('CHEQUE', 'Chèque'),
        ('VIREMENT', 'Virement Bancaire')
    ], validators=[DataRequired()])
    categorie_compte = SelectField('Catégorie', choices=[
        ('OFFICE', 'Compte Office'),
        ('CLIENT', 'Compte Client')
    ], validators=[DataRequired()])
    dossier = QuerySelectField('Dossier (optionnel)', query_factory=enabled_dossiers,
                               get_label='numero_dossier', allow_blank=True, blank_text='-- Aucun --')
    submit_btn = SubmitField('Enregistrer la Recette')

class DepenseForm(FlaskForm):
    """Simplified form for recording expenses."""
    date_operation = DateField('Date', validators=[DataRequired()])
    libelle = StringField('Libellé', validators=[DataRequired()])
    montant = DecimalField('Montant (FCFA)', validators=[DataRequired(), NumberRange(min=0)], places=2)
    mode_paiement = SelectField('Mode de Paiement', choices=[
        ('ESPECES', 'Espèces'),
        ('CHEQUE', 'Chèque'),
        ('VIREMENT', 'Virement Bancaire')
    ], validators=[DataRequired()])
    categorie_compte = SelectField('Catégorie', choices=[
        ('OFFICE', 'Compte Office'),
        ('CLIENT', 'Compte Client')
    ], validators=[DataRequired()])
    dossier = QuerySelectField('Dossier (optionnel)', query_factory=enabled_dossiers,
                               get_label='numero_dossier', allow_blank=True, blank_text='-- Aucun --')
    submit_btn = SubmitField('Enregistrer la Dépense')
