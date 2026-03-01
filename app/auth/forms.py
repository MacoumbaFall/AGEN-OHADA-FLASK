from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember_me = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nouveau mot de passe', validators=[DataRequired()])
    password_confirm = PasswordField('Confirmer le mot de passe', validators=[DataRequired()])
    submit = SubmitField('Réinitialiser le mot de passe')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Demander une réinitialisation')
