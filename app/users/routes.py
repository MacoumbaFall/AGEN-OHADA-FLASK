from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.users import bp
from app.users.forms import UserCreateForm, UserEditForm, ChangePasswordForm, AdminResetPasswordForm
from app.models import User, SecurityLog
from flask import request
from app.decorators import admin_required
from datetime import datetime


@bp.route('/')
@login_required
@admin_required
def index():
    """List all users - Admin only"""
    page = request.args.get('page', 1, type=int)
    users_query = db.select(User).order_by(User.created_at.desc())
    users_pagination = db.paginate(users_query, page=page, per_page=20, error_out=False)
    
    return render_template('users/index.html', 
                         title='Gestion des Utilisateurs',
                         users=users_pagination.items,
                         pagination=users_pagination)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """Create new user - Admin only"""
    form = UserCreateForm()
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        try:
            from app.email import send_email
            from flask import current_app
            
            token = user.get_reset_token()
            reset_url = url_for('auth.reset_password_token', token=token, _external=True)
            mail_subject = "Bienvenue sur AGEN-OHADA - Activez votre compte"
            mail_body = f"""Bonjour {user.username},
            
Votre compte a été créé avec succès par l'administrateur.
Veuillez cliquer sur le lien ci-dessous pour définir votre mot de passe et activer votre compte :
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
        except Exception as e:
            current_app.logger.error(f'Could not send welcome email : {str(e)}')
        
        flash(f'Utilisateur {user.username} créé avec succès.', 'success')
        return redirect(url_for('users.index'))
    
    return render_template('users/form.html', 
                         title='Nouvel Utilisateur',
                         form=form,
                         is_edit=False)


@bp.route('/<int:id>')
@login_required
@admin_required
def view(id):
    """View user details - Admin only"""
    user = db.session.get(User, id)
    if not user:
        flash('Utilisateur introuvable.', 'error')
        return redirect(url_for('users.index'))
    
    return render_template('users/view.html', 
                         title=f'Utilisateur: {user.username}',
                         user=user)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    """Edit user - Admin only"""
    user = db.session.get(User, id)
    if not user:
        flash('Utilisateur introuvable.', 'error')
        return redirect(url_for('users.index'))
    
    form = UserEditForm(user.username, user.email, obj=user)
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        
        db.session.commit()
        flash(f'Utilisateur {user.username} mis à jour.', 'success')
        return redirect(url_for('users.view', id=user.id))
    
    return render_template('users/form.html',
                         title=f'Modifier: {user.username}',
                         form=form,
                         user=user,
                         is_edit=True)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    """Delete user - Admin only"""
    user = db.session.get(User, id)
    if not user:
        flash('Utilisateur introuvable.', 'error')
        return redirect(url_for('users.index'))
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        flash('Vous ne pouvez pas supprimer votre propre compte.', 'error')
        return redirect(url_for('users.index'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'Utilisateur {username} supprimé.', 'success')
    return redirect(url_for('users.index'))


@bp.route('/profile')
@login_required
def profile():
    """View own profile - All authenticated users"""
    return render_template('users/profile.html',
                         title='Mon Profil',
                         user=current_user)


@bp.route('/profile/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change own password - All authenticated users"""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Mot de passe actuel incorrect.', 'error')
            return render_template('users/change_password.html',
                                 title='Changer le mot de passe',
                                 form=form)
        
        current_user.set_password(form.new_password.data)
        db.session.commit()
        
        flash('Votre mot de passe a été changé avec succès.', 'success')
        return redirect(url_for('users.profile'))
    
    return render_template('users/change_password.html',
                         title='Changer le mot de passe',
                         form=form)


@bp.route('/<int:id>/reset-password', methods=['GET', 'POST'])
@login_required
@admin_required
def reset_password(id):
    """Admin reset user password - Admin only"""
    user = db.session.get(User, id)
    if not user:
        flash('Utilisateur introuvable.', 'error')
        return redirect(url_for('users.index'))
    
    form = AdminResetPasswordForm()
    
    if form.validate_on_submit():
        user.set_password(form.new_password.data)
        db.session.commit()
        
        try:
            from app.email import send_email
            from flask import current_app
            
            token = user.get_reset_token()
            reset_url = url_for('auth.reset_password_token', token=token, _external=True)
            mail_subject = "Réinitialisation de votre mot de passe"
            mail_body = f"""Bonjour {user.username},
            
Votre mot de passe a été réinitialisé par un administrateur.
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
        except Exception as e:
            current_app.logger.error(f'Could not send reset password email : {str(e)}')
            
        flash(f'Mot de passe de {user.username} réinitialisé avec succès.', 'success')
        return redirect(url_for('users.view', id=user.id))
    
    return render_template('users/reset_password.html',
                         title=f'Réinitialiser le mot de passe: {user.username}',
                         form=form,
                         user=user)


@bp.route('/<int:id>/unlock', methods=['POST'])
@login_required
@admin_required
def unlock(id):
    """Unlock user account - Admin only"""
    user = db.session.get(User, id)
    if not user:
        flash('Utilisateur introuvable.', 'error')
        return redirect(url_for('users.index'))
    
    user.is_locked = False
    user.failed_login_attempts = 0
    
    # Log the unlock event
    from app.auth.routes import log_security_event
    log_security_event('ACCOUNT_UNLOCKED', user.username, details=f"Unlocked by admin: {current_user.username}")
    
    db.session.commit()
    
    flash(f'Le compte de {user.username} a été déverrouillé.', 'success')
    return redirect(url_for('users.view', id=user.id))

@bp.route('/security-logs')
@login_required
@admin_required
def security_logs():
    """Display security logs - Admin only"""
    page = request.args.get('page', 1, type=int)
    logs_query = db.select(SecurityLog).order_by(SecurityLog.timestamp.desc())
    logs_pagination = db.paginate(logs_query, page=page, per_page=50, error_out=False)
    
    return render_template('users/security_logs.html',
                         title='Logs de Sécurité',
                         logs=logs_pagination.items,
                         pagination=logs_pagination)


# ── Paramètres de l'étude ──────────────────────────────────────────────────
from app.users.routes_parametres import parametres_etude  # noqa: F401,E402
