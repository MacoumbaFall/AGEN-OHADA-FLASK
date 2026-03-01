from flask import render_template, flash, redirect, url_for, request, current_app, send_file, jsonify, abort
from flask_wtf.csrf import validate_csrf, ValidationError
from flask_login import login_required, current_user
from app.users import bp
from app.decorators import admin_required, role_required
from app.actes.services.parametres import ParametreService, DEFAULTS
from app.models import ParametreEtude, Formalite, Template
from app import db
import os


@bp.route('/parametres', methods=['GET', 'POST'])
@login_required
@admin_required
def parametres_etude():
    """Page de configuration des paramètres de l'étude — ADMIN uniquement."""

    if request.method == 'POST':
        # Manual CSRF Protection (SEC-07)
        try:
            validate_csrf(request.form.get('csrf_token'))
        except ValidationError:
            abort(400, "Jeton CSRF invalide.")
        
        updated = 0
        errors = []

        for cle in DEFAULTS:
            nouvelle_valeur = request.form.get(cle, '').strip()
            if not nouvelle_valeur:
                continue

            # Validation selon le type attendu
            type_v = DEFAULTS[cle].get('type_valeur', 'string')
            try:
                if type_v == 'decimal':
                    from decimal import Decimal, InvalidOperation
                    Decimal(nouvelle_valeur)  # validation
                elif type_v == 'int':
                    int(nouvelle_valeur)
            except (ValueError, Exception):
                errors.append(f"Valeur invalide pour « {DEFAULTS[cle]['libelle']} » : {nouvelle_valeur}")
                continue

            ParametreService.set(cle, nouvelle_valeur, user_id=current_user.id)
            updated += 1

        if errors:
            for err in errors:
                flash(err, 'error')
        if updated:
            flash(f'{updated} paramètre(s) mis à jour avec succès.', 'success')

        return redirect(url_for('users.parametres_etude'))

    # Chargement depuis la DB (ou fallback DEFAULTS)
    rows = db.session.execute(db.select(ParametreEtude).order_by(ParametreEtude.groupe, ParametreEtude.cle)).scalars().all()
    db_map = {r.cle: r for r in rows}

    # Regrouper par groupe pour l'affichage
    groupes = {}
    groupe_labels = {
        'FISCAL':   ('🏦 Taux Fiscaux',              'Taux TVA, Conservation Foncière, enregistrement'),
        'MUTATION': ('🏠 Droits de Mutation',         'Seuils et montants des droits de mutation immobilière'),
        'DEBOURS':  ('💼 Débours Standards',           'Frais d\'expéditions, publicité, morcellement, divers'),
        'BAREMES':  ('📊 Seuils Barèmes Honoraires',   'Montants des tranches (0-20M, 20-80M, etc.)'),
        'FACTURATION': ('🧾 Facturation',               'Mentions légales, coordonnées bancaires, délais'),
        'ETUDE':    ('🏛️ Identité de l\'Étude',       'Nom, adresse, coordonnées du notaire'),
    }

    for cle, meta in DEFAULTS.items():
        groupe = meta.get('groupe', 'FISCAL')
        if groupe not in groupes:
            groupes[groupe] = []
        groupes[groupe].append({
            'cle': cle,
            'libelle': meta['libelle'],
            'description': meta.get('description', ''),
            'type_valeur': meta.get('type_valeur', 'string'),
            'valeur': db_map[cle].valeur if cle in db_map else meta['valeur'],
            'modifie_le': db_map[cle].updated_at if cle in db_map else None,
        })

    return render_template(
        'users/parametres_etude.html',
        title='Paramètres de l\'Étude',
        groupes=groupes,
        groupe_labels=groupe_labels,
    )
