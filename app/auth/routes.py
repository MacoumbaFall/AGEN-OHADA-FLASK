from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user
from urllib.parse import urlparse
from datetime import datetime
from app import db, limiter
from app.auth import bp
from app.auth.forms import LoginForm, ResetPasswordForm, ResetPasswordRequestForm
from app.models import User, SecurityLog

def log_security_event(event_type, username, details=None):
    log = SecurityLog(
        event_type=event_type,
        username=username,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        details=details
    )
    db.session.add(log)
    # Note: we don't commit here because we'll commit with the user changes usually

@bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            db.select(User).where(User.email == form.email.data))
        if user:
            # Reusing existing logic to send token
            from app.email import send_email
            from flask import current_app
            token = user.get_reset_token()
            reset_url = url_for('auth.reset_password_token', token=token, _external=True)
            mail_subject = "Réinitialisation de votre mot de passe"
            mail_body = f"""Bonjour {user.username},
            
Veuillez cliquer sur le lien ci-dessous pour choisir votre nouveau mot de passe :
{reset_url}

Ce lien expirera dans 30 minutes.

Cordialement,
L'équipe AGEN-OHADA.
"""
            send_email(
                subject=mail_subject,
                sender=current_app.config['ADMINS'][0],
                recipients=[user.email],
                text_body=mail_body
            )
        # Always flash the same message to prevent email enumeration
        flash('Consultez votre boîte mail pour les instructions de réinitialisation.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', title='Réinitialiser MDP', form=form)

@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            db.select(User).where(User.username == form.username.data))
        
        if user:
            # 1. Check for Throttling (Admin) or Permanent Lock (Others)
            if not user.can_attempt_login():
                if user.role == 'ADMIN':
                    delay = user.get_throttling_delay()
                    flash(f'Tentative trop rapide. Veuillez attendre {delay} secondes.', 'warning')
                else:
                    flash('Ce compte est verrouillé suite à trop de tentatives infructueuses. Veuillez contacter un administrateur.', 'error')
                return redirect(url_for('auth.login'))
            
            # 2. Check Password
            if user.check_password(form.password.data):
                # Success
                user.last_login = datetime.utcnow()
                user.failed_login_attempts = 0
                user.last_failed_login = None
                log_security_event('LOGIN_SUCCESS', user.username)
                db.session.commit()
                
                login_user(user, remember=form.remember_me.data)
                next_page = request.args.get('next')
                if not next_page or urlparse(next_page).netloc != '':
                    next_page = url_for('main.index')
                return redirect(next_page)
            else:
                # Failure
                user.failed_login_attempts += 1
                user.last_failed_login = datetime.utcnow()
                
                if user.role == 'ADMIN':
                    from flask import current_app
                    current_app.logger.warning(f"FAILED LOGIN ATTEMPT: Admin '{user.username}' (Total: {user.failed_login_attempts})")
                    log_security_event('LOGIN_FAILED', user.username, details=f"Admin attempt {user.failed_login_attempts}")
                    
                    if user.failed_login_attempts >= 5:
                        delay = user.get_throttling_delay()
                        flash(f'Échec Admin. Délai imposé : {delay}s. En cas d\'oubli, utilisez "Mot de passe oublié" pour recevoir un lien par email.', 'warning')
                    else:
                        flash(f'Identifiants Administrateur invalides. Tentative {user.failed_login_attempts}/5 avant délai.', 'warning')
                else:
                    if user.failed_login_attempts >= 5:
                        user.is_locked = True
                        log_security_event('ACCOUNT_LOCKED', user.username, details=f"Failed attempts threshold reached")
                        flash('Compte verrouillé : trop de tentatives infructueuses. Veuillez contacter un administrateur.', 'error')
                    else:
                        log_security_event('LOGIN_FAILED', user.username, details=f"Attempt {user.failed_login_attempts}")
                        flash(f'Nom d\'utilisateur ou mot de passe invalide. Tentatives restantes : {5 - user.failed_login_attempts}')
                
                db.session.commit()
        else:
            flash('Nom d\'utilisateur ou mot de passe invalide')
            
        return redirect(url_for('auth.login'))
    return render_template('auth/login.html', title='Connexion', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_token(token)
    if not user:
        flash('Le lien de réinitialisation est invalide ou a expiré.', 'error')
        return redirect(url_for('auth.login'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        if form.password.data != form.password_confirm.data:
            flash('Les mots de passe ne correspondent pas.', 'error')
            return render_template('auth/reset_password_token.html', form=form)
        user.set_password(form.password.data)
        db.session.commit()
        flash('Votre mot de passe a été réinitialisé. Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_token.html', form=form)

