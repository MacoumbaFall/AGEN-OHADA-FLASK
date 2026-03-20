from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    """Decorator to require ADMIN role or ADMIN permission"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Veuillez vous connecter pour accéder à cette page.', 'error')
            return redirect(url_for('auth.login'))
        if current_user.role != 'ADMIN' and not current_user.has_permission('ADMIN'):
            flash('Accès refusé. Privilèges administrateur requis.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    """Decorator to require one of the specified roles or corresponding permissions"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Veuillez vous connecter pour accéder à cette page.', 'error')
                return redirect(url_for('auth.login'))
            
            if current_user.role in roles:
                return f(*args, **kwargs)
            
            # Map roles to common permissions to allow custom profiles to access legacy routes
            implied_perms = []
            if 'ADMIN' in roles: implied_perms.append('ADMIN')
            
            # Let's map routes checking NOTAIRE/CLERC/ADMIN to generic action permissions
            # Often dossiers use ('NOTAIRE', 'CLERC', 'ADMIN')
            if 'CLERC' in roles or 'NOTAIRE' in roles: implied_perms.append('MANAGE_DOSSIERS')
            if 'COMPTABLE' in roles: implied_perms.append('MANAGE_COMPTA')
            if 'SECRETAIRE' in roles: implied_perms.append('MANAGE_CLIENTS')
            
            # Specific case for notaire-only
            if 'NOTAIRE' in roles and 'CLERC' not in roles:
                implied_perms.append('SIGNER_ACTES')
            
            if any(current_user.has_permission(p) for p in implied_perms):
                return f(*args, **kwargs)
                
            flash(f'Accès refusé. Privilèges insuffisants pour cette action.', 'error')
            return redirect(url_for('main.index'))
        return decorated_function
    return decorator
