from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, BooleanField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from app.models import User, Profile

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class ProfileForm(FlaskForm):
    code = StringField('Code Profil', validators=[
        DataRequired(message='Le code est requis'),
        Length(min=3, max=50)
    ])
    nom = StringField('Nom Profil', validators=[
        DataRequired(message='Le nom est requis'),
        Length(min=3, max=100)
    ])
    description = StringField('Description')
    permissions = MultiCheckboxField('Fonctionnalités', coerce=int)
    submit = SubmitField('Enregistrer')

    def __init__(self, original_code=None, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.original_code = original_code
        from app import db
        from app.models import Permission
        perms = db.session.scalars(db.select(Permission).order_by(Permission.nom)).all()
        self.permissions.choices = [(p.id, f"{p.nom} - {p.description or ''}") for p in perms]

    def validate_code(self, code):
        if self.original_code is None or code.data != self.original_code:
            from app import db
            profile = db.session.scalar(db.select(Profile).where(Profile.code == code.data))
            if profile:
                raise ValidationError('Ce code de profil existe déjà.')


class UserCreateForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[
        DataRequired(message='Le nom d\'utilisateur est requis'),
        Length(min=3, max=50, message='Le nom d\'utilisateur doit contenir entre 3 et 50 caractères')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='L\'email est requis'),
        Email(message='Email invalide')
    ])
    password = PasswordField('Mot de passe', validators=[
        DataRequired(message='Le mot de passe est requis'),
        Length(min=6, message='Le mot de passe doit contenir au moins 6 caractères')
    ])
    password_confirm = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(message='Veuillez confirmer le mot de passe'),
        EqualTo('password', message='Les mots de passe ne correspondent pas')
    ])
    role = SelectField('Profil', validators=[DataRequired(message='Le rôle est requis')])
    submit = SubmitField('Créer l\'utilisateur')

    def __init__(self, *args, **kwargs):
        super(UserCreateForm, self).__init__(*args, **kwargs)
        from app import db
        from app.models import Profile
        profiles = db.session.scalars(db.select(Profile).order_by(Profile.nom)).all()
        if profiles:
            self.role.choices = [(p.code, p.nom) for p in profiles]
        else:
            self.role.choices = [
                ('NOTAIRE', 'Notaire'),
                ('CLERC', 'Clerc'),
                ('COMPTABLE', 'Comptable'),
                ('SECRETAIRE', 'Secrétaire'),
                ('ADMIN', 'Administrateur')
            ]

    def validate_username(self, username):
        from app import db
        user = db.session.scalar(db.select(User).where(User.username == username.data))
        if user:
            raise ValidationError('Ce nom d\'utilisateur est déjà utilisé.')

    def validate_email(self, email):
        from app import db
        user = db.session.scalar(db.select(User).where(User.email == email.data))
        if user:
            raise ValidationError('Cet email est déjà utilisé.')


class UserEditForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[
        DataRequired(message='Le nom d\'utilisateur est requis'),
        Length(min=3, max=50, message='Le nom d\'utilisateur doit contenir entre 3 et 50 caractères')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='L\'email est requis'),
        Email(message='Email invalide')
    ])
    role = SelectField('Profil', validators=[DataRequired(message='Le rôle est requis')])
    submit = SubmitField('Mettre à jour')

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email
        from app import db
        from app.models import Profile
        profiles = db.session.scalars(db.select(Profile).order_by(Profile.nom)).all()
        if profiles:
            self.role.choices = [(p.code, p.nom) for p in profiles]
        else:
            self.role.choices = [
                ('NOTAIRE', 'Notaire'),
                ('CLERC', 'Clerc'),
                ('COMPTABLE', 'Comptable'),
                ('SECRETAIRE', 'Secrétaire'),
                ('ADMIN', 'Administrateur')
            ]

    def validate_username(self, username):
        if username.data != self.original_username:
            from app import db
            user = db.session.scalar(db.select(User).where(User.username == username.data))
            if user:
                raise ValidationError('Ce nom d\'utilisateur est déjà utilisé.')

    def validate_email(self, email):
        if email.data != self.original_email:
            from app import db
            user = db.session.scalar(db.select(User).where(User.email == email.data))
            if user:
                raise ValidationError('Cet email est déjà utilisé.')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Mot de passe actuel', validators=[
        DataRequired(message='Le mot de passe actuel est requis')
    ])
    new_password = PasswordField('Nouveau mot de passe', validators=[
        DataRequired(message='Le nouveau mot de passe est requis'),
        Length(min=6, message='Le mot de passe doit contenir au moins 6 caractères')
    ])
    new_password_confirm = PasswordField('Confirmer le nouveau mot de passe', validators=[
        DataRequired(message='Veuillez confirmer le nouveau mot de passe'),
        EqualTo('new_password', message='Les mots de passe ne correspondent pas')
    ])
    submit = SubmitField('Changer le mot de passe')


class AdminResetPasswordForm(FlaskForm):
    """Admin can reset user password without knowing current password"""
    new_password = PasswordField('Nouveau mot de passe', validators=[
        DataRequired(message='Le nouveau mot de passe est requis'),
        Length(min=6, message='Le mot de passe doit contenir au moins 6 caractères')
    ])
    new_password_confirm = PasswordField('Confirmer le nouveau mot de passe', validators=[
        DataRequired(message='Veuillez confirmer le nouveau mot de passe'),
        EqualTo('new_password', message='Les mots de passe ne correspondent pas')
    ])
    submit = SubmitField('Réinitialiser le mot de passe')
