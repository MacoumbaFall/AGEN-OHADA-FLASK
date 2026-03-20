from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.users import bp
from app.users.forms import ProfileForm
from app.models import Profile, Permission, User
from app.decorators import admin_required


@bp.route('/profiles')
@login_required
@admin_required
def profiles_index():
    """List all profiles - Admin only"""
    profiles = db.session.scalars(
        db.select(Profile).order_by(Profile.is_predefined.desc(), Profile.nom)
    ).all()
    return render_template('users/profiles/index.html',
                           title='Gestion des Profils',
                           profiles=profiles)


@bp.route('/profiles/create', methods=['GET', 'POST'])
@login_required
@admin_required
def profiles_create():
    """Create a new custom profile - Admin only"""
    form = ProfileForm()

    if form.validate_on_submit():
        # Prevent using reserved predefined codes
        reserved_codes = {'ADMIN', 'NOTAIRE', 'CLERC', 'COMPTABLE', 'SECRETAIRE'}
        if form.code.data.upper() in reserved_codes:
            flash(f'Le code "{form.code.data.upper()}" est réservé aux profils prédéfinis.', 'error')
            return render_template('users/profiles/form.html',
                                   title='Nouveau Profil',
                                   form=form,
                                   is_edit=False)

        profile = Profile(
            code=form.code.data.upper(),
            nom=form.nom.data,
            description=form.description.data,
            is_predefined=False
        )
        # Assign permissions
        if form.permissions.data:
            selected_perms = db.session.scalars(
                db.select(Permission).where(Permission.id.in_(form.permissions.data))
            ).all()
            profile.permissions = selected_perms

        db.session.add(profile)
        db.session.commit()
        flash(f'Profil "{profile.nom}" créé avec succès.', 'success')
        return redirect(url_for('users.profiles_index'))

    return render_template('users/profiles/form.html',
                           title='Nouveau Profil',
                           form=form,
                           is_edit=False)


@bp.route('/profiles/<int:id>')
@login_required
@admin_required
def profiles_view(id):
    """View a profile's details - Admin only"""
    profile = db.session.get(Profile, id)
    if not profile:
        flash('Profil introuvable.', 'error')
        return redirect(url_for('users.profiles_index'))

    # Count users with this profile
    users_count = db.session.scalar(
        db.select(db.func.count(User.id)).where(User.role == profile.code)
    ) or 0

    return render_template('users/profiles/view.html',
                           title=f'Profil: {profile.nom}',
                           profile=profile,
                           users_count=users_count)


@bp.route('/profiles/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def profiles_edit(id):
    """Edit a profile - Admin only. Predefined profiles: only permissions can be changed."""
    profile = db.session.get(Profile, id)
    if not profile:
        flash('Profil introuvable.', 'error')
        return redirect(url_for('users.profiles_index'))

    form = ProfileForm(original_code=profile.code, obj=profile)

    if form.validate_on_submit():
        # For predefined profiles, only permissions can be updated
        if not profile.is_predefined:
            reserved_codes = {'ADMIN', 'NOTAIRE', 'CLERC', 'COMPTABLE', 'SECRETAIRE'}
            new_code = form.code.data.upper()
            if new_code in reserved_codes and new_code != profile.code:
                flash(f'Le code "{new_code}" est réservé aux profils prédéfinis.', 'error')
                return render_template('users/profiles/form.html',
                                       title=f'Modifier: {profile.nom}',
                                       form=form,
                                       profile=profile,
                                       is_edit=True)
            profile.code = new_code
            profile.nom = form.nom.data
            profile.description = form.description.data

        # Update permissions for all profiles (predefined or not)
        selected_perms = db.session.scalars(
            db.select(Permission).where(Permission.id.in_(form.permissions.data or []))
        ).all()
        profile.permissions = selected_perms

        db.session.commit()
        flash(f'Profil "{profile.nom}" mis à jour avec succès.', 'success')
        return redirect(url_for('users.profiles_view', id=profile.id))

    # Pre-select existing permissions
    if request.method == 'GET':
        form.permissions.data = [p.id for p in profile.permissions]

    return render_template('users/profiles/form.html',
                           title=f'Modifier: {profile.nom}',
                           form=form,
                           profile=profile,
                           is_edit=True)


@bp.route('/profiles/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def profiles_delete(id):
    """Delete a custom profile - Admin only. Cannot delete predefined profiles."""
    profile = db.session.get(Profile, id)
    if not profile:
        flash('Profil introuvable.', 'error')
        return redirect(url_for('users.profiles_index'))

    if profile.is_predefined:
        flash('Impossible de supprimer un profil prédéfini.', 'error')
        return redirect(url_for('users.profiles_index'))

    # Check if users are assigned this profile
    users_count = db.session.scalar(
        db.select(db.func.count(User.id)).where(User.role == profile.code)
    ) or 0

    if users_count > 0:
        flash(f'Impossible de supprimer ce profil : {users_count} utilisateur(s) lui sont assignés. '
              f'Veuillez d\'abord réassigner ces utilisateurs à un autre profil.', 'error')
        return redirect(url_for('users.profiles_view', id=profile.id))

    nom = profile.nom
    db.session.delete(profile)
    db.session.commit()
    flash(f'Profil "{nom}" supprimé avec succès.', 'success')
    return redirect(url_for('users.profiles_index'))
