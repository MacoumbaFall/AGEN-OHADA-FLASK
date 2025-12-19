from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from app.models import User

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
    role = SelectField('Rôle', choices=[
        ('NOTAIRE', 'Notaire'),
        ('CLERC', 'Clerc'),
        ('COMPTABLE', 'Comptable'),
        ('SECRETAIRE', 'Secrétaire'),
        ('ADMIN', 'Administrateur')
    ], validators=[DataRequired(message='Le rôle est requis')])
    submit = SubmitField('Créer l\'utilisateur')

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
    role = SelectField('Rôle', choices=[
        ('NOTAIRE', 'Notaire'),
        ('CLERC', 'Clerc'),
        ('COMPTABLE', 'Comptable'),
        ('SECRETAIRE', 'Secrétaire'),
        ('ADMIN', 'Administrateur')
    ], validators=[DataRequired(message='Le rôle est requis')])
    submit = SubmitField('Mettre à jour')

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

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
