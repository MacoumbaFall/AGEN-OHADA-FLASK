from datetime import datetime
from typing import Optional
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Text, Date, Boolean, Numeric, TIMESTAMP, JSON
# from sqlalchemy.dialects.postgresql import JSONB
from app import db, login

class Permission(db.Model):
    __tablename__ = 'permissions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

class ProfilePermission(db.Model):
    __tablename__ = 'profile_permissions'
    profile_id: Mapped[int] = mapped_column(ForeignKey('profiles.id', ondelete='CASCADE'), primary_key=True)
    permission_id: Mapped[int] = mapped_column(ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True)

class Profile(db.Model):
    __tablename__ = 'profiles'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False) # e.g. NOTAIRE, CLERC, ADMIN ou nouveau code
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_predefined: Mapped[bool] = mapped_column(Boolean, default=False)
    
    permissions = relationship('Permission', secondary='profile_permissions', backref='profiles')
    users = relationship('User', back_populates='profile_relation', primaryjoin="Profile.code == foreign(User.role)")


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False) # 'NOTAIRE', 'CLERC', 'COMPTABLE', 'ADMIN', 'SECRETAIRE'
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    last_login: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_failed_login: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)

    dossiers = relationship('Dossier', back_populates='responsable')
    ecritures = relationship('ComptaEcriture', back_populates='auteur')
    profile_relation = relationship('Profile', back_populates='users', primaryjoin="User.role == Profile.code", foreign_keys=[role])

    @property
    def user_permissions(self):
        if hasattr(self, '_user_permissions'):
            return self._user_permissions
        if self.profile_relation:
            self._user_permissions = [p.code for p in self.profile_relation.permissions]
        else:
            self._user_permissions = []
        return self._user_permissions

    def has_permission(self, perm_code):
        if self.role == 'ADMIN':
            return True
        return perm_code in self.user_permissions

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_throttling_delay(self):
        """Calculate exponential backoff delay in seconds: 2^(n-5)"""
        if self.role != 'ADMIN' or self.failed_login_attempts < 5:
            return 0
        return 2 ** (self.failed_login_attempts - 5)

    def can_attempt_login(self):
        """Check if enough time has passed since last failed login (for Admins)"""
        if self.role != 'ADMIN' or self.failed_login_attempts < 5:
            return not self.is_locked
        
        if not self.last_failed_login:
            return True
            
        import datetime as dt
        delay = self.get_throttling_delay()
        next_allowed = self.last_failed_login + dt.timedelta(seconds=delay)
        return datetime.utcnow() >= next_allowed

    def get_reset_token(self, expires_sec=1800):
        from itsdangerous import URLSafeTimedSerializer
        from flask import current_app
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token):
        from itsdangerous import URLSafeTimedSerializer
        from flask import current_app
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=1800)['user_id']
        except:
            return None
        return db.session.get(User, user_id)

    def __repr__(self):
        return f'<User {self.username}>'

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class Client(db.Model):
    __tablename__ = 'clients'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type_client: Mapped[str] = mapped_column(String(20), nullable=False) # 'PHYSIQUE', 'MORALE'
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    prenom: Mapped[Optional[str]] = mapped_column(String(100))
    date_naissance: Mapped[Optional[datetime]] = mapped_column(Date)
    lieu_naissance: Mapped[Optional[str]] = mapped_column(String(100))
    adresse: Mapped[Optional[str]] = mapped_column(Text)
    telephone: Mapped[Optional[str]] = mapped_column(String(30))
    email: Mapped[Optional[str]] = mapped_column(String(100))
    identifiant_unique: Mapped[Optional[str]] = mapped_column(String(50))
    
    # --- Personne Physique ---
    profession: Mapped[Optional[str]] = mapped_column(String(100))
    nationalite: Mapped[Optional[str]] = mapped_column(String(50))
    situation_matrimoniale: Mapped[Optional[str]] = mapped_column(String(50))
    regime_matrimonial: Mapped[Optional[str]] = mapped_column(String(100))
    
    # --- Personne Morale ---
    forme_juridique: Mapped[Optional[str]] = mapped_column(String(50))
    capital_social: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    rccm: Mapped[Optional[str]] = mapped_column(String(100))
    ninea: Mapped[Optional[str]] = mapped_column(String(100))
    
    # --- KYC / Pièces d'identité ---
    type_piece_identite: Mapped[Optional[str]] = mapped_column(String(50))
    numero_piece_identite: Mapped[Optional[str]] = mapped_column(String(100))
    date_emission_piece: Mapped[Optional[datetime]] = mapped_column(Date)
    date_expiration_piece: Mapped[Optional[datetime]] = mapped_column(Date)
    autorite_emission_piece: Mapped[Optional[str]] = mapped_column(String(100))
    
    # --- Statut KYC ---
    kyc_statut: Mapped[str] = mapped_column(String(20), default='A_VERIFIER') # 'A_VERIFIER', 'VALIDE', 'EXPIRE', 'REJETE'
    kyc_date_verification: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    kyc_notes: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    dossier_participations = relationship('DossierParty', back_populates='client')

class SecurityLog(db.Model):
    __tablename__ = 'security_logs'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False) # 'LOGIN_SUCCESS', 'LOGIN_FAILED', 'ACCOUNT_LOCKED', 'ACCOUNT_UNLOCKED'
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(String(255))
    details: Mapped[Optional[str]] = mapped_column(Text)
    
    # Audit trail (Actions utilisateurs, entités et champs modifiés)
    target_resource: Mapped[Optional[str]] = mapped_column(String(100)) # e.g. 'clients', 'dossiers'
    target_id: Mapped[Optional[str]] = mapped_column(String(50)) # The ID of the modified entity
    changes: Mapped[Optional[dict]] = mapped_column(JSON) # JSON object showing old vs new values

    def __repr__(self):
        return f'<SecurityLog {self.event_type} - {self.username}>'
    


class Dossier(db.Model):
    __tablename__ = 'dossiers'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    numero_dossier: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    intitule: Mapped[str] = mapped_column(String(200), nullable=False)
    type_dossier: Mapped[Optional[str]] = mapped_column(String(50))
    statut: Mapped[str] = mapped_column(String(30), default='OUVERT')
    date_ouverture: Mapped[datetime] = mapped_column(Date, default=datetime.utcnow)
    date_cloture: Mapped[Optional[datetime]] = mapped_column(Date)
    responsable_id: Mapped[Optional[int]] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    responsable = relationship('User', back_populates='dossiers')
    parties = relationship('DossierParty', back_populates='dossier', cascade='all, delete-orphan')
    actes = relationship('Acte', back_populates='dossier', cascade='all, delete-orphan')
    ecritures = relationship('ComptaEcriture', back_populates='dossier')
    formalites = relationship('Formalite', back_populates='dossier', cascade='all, delete-orphan')

class DossierParty(db.Model):
    __tablename__ = 'dossier_parties'

    dossier_id: Mapped[int] = mapped_column(ForeignKey('dossiers.id', ondelete='CASCADE'), primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey('clients.id', ondelete='CASCADE'), primary_key=True)
    role_dans_acte: Mapped[str] = mapped_column(String(50), nullable=False)

    dossier = relationship('Dossier', back_populates='parties')
    client = relationship('Client', back_populates='dossier_participations')


class ComptaCompte(db.Model):
    __tablename__ = 'compta_comptes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    numero_compte: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    libelle: Mapped[str] = mapped_column(String(100), nullable=False)
    type_compte: Mapped[str] = mapped_column(String(20), nullable=False) # 'GENERAL', 'CLIENT', 'TIERS'
    categorie: Mapped[Optional[str]] = mapped_column(String(20)) # 'OFFICE', 'CLIENT' for strict separation
    actif: Mapped[bool] = mapped_column(Boolean, default=True)

    mouvements = relationship('ComptaMouvement', back_populates='compte')

    def get_solde(self):
        """Calculate the current balance of the account."""
        total_debit = sum(m.debit for m in self.mouvements if m.ecriture.valide)
        total_credit = sum(m.credit for m in self.mouvements if m.ecriture.valide)
        return total_debit - total_credit

class ComptaEcriture(db.Model):
    __tablename__ = 'compta_ecritures'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    numero_piece: Mapped[Optional[str]] = mapped_column(String(50)) # Receipt/Invoice number
    date_ecriture: Mapped[datetime] = mapped_column(Date, default=datetime.utcnow, nullable=False)
    libelle_operation: Mapped[str] = mapped_column(String(200), nullable=False)
    dossier_id: Mapped[Optional[int]] = mapped_column(ForeignKey('dossiers.id'))
    journal_code: Mapped[str] = mapped_column(String(10), nullable=False) # 'BQ', 'CA', 'OD', 'VT'
    valide: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    dossier = relationship('Dossier', back_populates='ecritures')
    auteur = relationship('User', back_populates='ecritures')
    mouvements = relationship('ComptaMouvement', back_populates='ecriture', cascade='all, delete-orphan')

    def is_balanced(self):
        """Check if the entry is balanced (total debits = total credits)."""
        total_debit = sum(m.debit for m in self.mouvements)
        total_credit = sum(m.credit for m in self.mouvements)
        return abs(total_debit - total_credit) < 0.01  # Allow for rounding errors

    def get_total(self):
        """Get the total amount of the transaction."""
        return sum(m.debit for m in self.mouvements)

class ComptaMouvement(db.Model):
    __tablename__ = 'compta_mouvements'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ecriture_id: Mapped[int] = mapped_column(ForeignKey('compta_ecritures.id', ondelete='CASCADE'))
    compte_id: Mapped[Optional[int]] = mapped_column(ForeignKey('compta_comptes.id'))
    debit: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    credit: Mapped[float] = mapped_column(Numeric(15, 2), default=0)

    ecriture = relationship('ComptaEcriture', back_populates='mouvements')
    compte = relationship('ComptaCompte', back_populates='mouvements')

class Recu(db.Model):
    """Model for receipts (Reçus)."""
    __tablename__ = 'recus'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    numero_recu: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    date_emission: Mapped[datetime] = mapped_column(Date, default=datetime.utcnow, nullable=False)
    dossier_id: Mapped[Optional[int]] = mapped_column(ForeignKey('dossiers.id'))
    client_id: Mapped[Optional[int]] = mapped_column(ForeignKey('clients.id'))
    montant: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    mode_paiement: Mapped[str] = mapped_column(String(20), nullable=False) # 'ESPECES', 'CHEQUE', 'VIREMENT'
    reference_paiement: Mapped[Optional[str]] = mapped_column(String(100)) # Check number, transfer ref, etc.
    motif: Mapped[str] = mapped_column(Text, nullable=False)
    ecriture_id: Mapped[Optional[int]] = mapped_column(ForeignKey('compta_ecritures.id'))
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    dossier = relationship('Dossier')
    client = relationship('Client')
    ecriture = relationship('ComptaEcriture')
    auteur = relationship('User')

class Facture(db.Model):
    """Model for invoices (Factures)."""
    __tablename__ = 'factures'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    numero_facture: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    date_emission: Mapped[datetime] = mapped_column(Date, default=datetime.utcnow, nullable=False)
    date_echeance: Mapped[Optional[datetime]] = mapped_column(Date)
    dossier_id: Mapped[Optional[int]] = mapped_column(ForeignKey('dossiers.id'))
    client_id: Mapped[Optional[int]] = mapped_column(ForeignKey('clients.id'))
    montant_ht: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    montant_tva: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    montant_ttc: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    statut: Mapped[str] = mapped_column(String(20), default='IMPAYEE') # 'IMPAYEE', 'PAYEE', 'ANNULEE'
    description: Mapped[str] = mapped_column(Text, nullable=False)
    ecriture_id: Mapped[Optional[int]] = mapped_column(ForeignKey('compta_ecritures.id'))
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    dossier = relationship('Dossier')
    client = relationship('Client')
    ecriture = relationship('ComptaEcriture')
    auteur = relationship('User')

class TypeFormalite(db.Model):
    __tablename__ = 'type_formalites'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nom: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    cout_base: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    delai_moyen: Mapped[Optional[int]] = mapped_column(Integer) # en jours

    formalites = relationship('Formalite', back_populates='type_relation')

class Formalite(db.Model):
    __tablename__ = 'formalites'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dossier_id: Mapped[Optional[int]] = mapped_column(ForeignKey('dossiers.id', ondelete='CASCADE'))
    type_formalite: Mapped[str] = mapped_column(String(100), nullable=False) # Legacy field
    type_id: Mapped[Optional[int]] = mapped_column(ForeignKey('type_formalites.id'))
    date_depot: Mapped[Optional[datetime]] = mapped_column(Date)
    date_retour: Mapped[Optional[datetime]] = mapped_column(Date)
    cout_estime: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    cout_reel: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    reference_externe: Mapped[Optional[str]] = mapped_column(String(100))
    statut: Mapped[str] = mapped_column(String(30), default='A_FAIRE')

    dossier = relationship('Dossier', back_populates='formalites')
    type_relation = relationship('TypeFormalite', back_populates='formalites')

class Template(db.Model):
    __tablename__ = 'templates'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    contenu: Mapped[Optional[str]] = mapped_column(Text) # Jinja2/HTML content (for legacy MD)
    file_path: Mapped[Optional[str]] = mapped_column(String(255)) # Path to .docx file
    is_docx: Mapped[bool] = mapped_column(Boolean, default=False)
    type_acte_id: Mapped[Optional[int]] = mapped_column(ForeignKey('type_actes.id'))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    type_acte = relationship('TypeActe', back_populates='templates')

class TypeActe(db.Model):
    __tablename__ = 'type_actes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nom: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    templates = relationship('Template', back_populates='type_acte')
    actes = relationship('Acte', back_populates='type_acte_relation')



# Update Acte model to include type_acte_id
class Acte(db.Model):
    __tablename__ = 'actes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dossier_id: Mapped[Optional[int]] = mapped_column(ForeignKey('dossiers.id', ondelete='CASCADE'))
    type_acte: Mapped[str] = mapped_column(String(100), nullable=False) # Keep original string for legacy/fallback
    type_acte_id: Mapped[Optional[int]] = mapped_column(ForeignKey('type_actes.id'))
    contenu_json: Mapped[Optional[dict]] = mapped_column(JSON)
    contenu_html: Mapped[Optional[str]] = mapped_column(Text)
    statut: Mapped[str] = mapped_column(String(30), default='BROUILLON')
    date_signature: Mapped[Optional[datetime]] = mapped_column(Date)
    
    # Finalization and Signature fields
    finalise_par_id: Mapped[Optional[int]] = mapped_column(ForeignKey('users.id'))
    date_finalisation: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    signature_electronique: Mapped[Optional[str]] = mapped_column(Text) # Placeholder for hash/signature
    
    # Archiving and Repertoire fields
    numero_repertoire: Mapped[Optional[int]] = mapped_column(Integer)
    date_archivage: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    archive_par_id: Mapped[Optional[int]] = mapped_column(ForeignKey('users.id'))
    
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    dossier = relationship('Dossier', back_populates='actes')
    type_acte_relation = relationship('TypeActe', back_populates='actes')
    finalise_par = relationship('User', foreign_keys=[finalise_par_id])
    archive_par = relationship('User', foreign_keys=[archive_par_id])


class ParametreEtude(db.Model):
    """
    Paramètres configurables de l'étude notariale.

    Table clé/valeur permettant de configurer les taux fiscaux,
    frais fixes et informations de l'étude directement depuis l'interface
    admin — sans modifier le code ni redémarrer le serveur.

    Groupes de paramètres :
      FISCAL    → taux TVA, droits d'enregistrement, Conservation Foncière
      MUTATION  → seuils et montants des droits de mutation
      DEBOURS   → frais d'expéditions, publicité, morcellement, etc.
      ETUDE     → nom, adresse, téléphone du notaire
    """
    __tablename__ = 'parametres_etude'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cle: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    valeur: Mapped[str] = mapped_column(Text, nullable=False)  # toujours stocké en string
    type_valeur: Mapped[str] = mapped_column(String(20), default='decimal')  # 'decimal', 'int', 'string', 'bool'
    groupe: Mapped[str] = mapped_column(String(30), default='FISCAL')  # 'FISCAL', 'MUTATION', 'DEBOURS', 'ETUDE'
    libelle: Mapped[str] = mapped_column(String(200), nullable=False)  # label affiché dans l'UI
    description: Mapped[Optional[str]] = mapped_column(Text)  # aide contextuelle
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by: Mapped[Optional[int]] = mapped_column(ForeignKey('users.id'))

    @property
    def valeur_typee(self):
        """Retourne la valeur dans son type natif (Decimal, int, str, bool)."""
        from decimal import Decimal
        if self.type_valeur == 'decimal':
            return Decimal(self.valeur)
        elif self.type_valeur == 'int':
            return int(self.valeur)
        elif self.type_valeur == 'bool':
            return self.valeur.lower() in ('true', '1', 'oui')
        return self.valeur  # string par défaut

    def __repr__(self):
        return f'<ParametreEtude {self.cle}={self.valeur}>'

