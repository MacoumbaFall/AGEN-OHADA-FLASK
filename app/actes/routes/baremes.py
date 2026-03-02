from flask import render_template, flash, redirect, url_for, request, current_app, abort
from flask_wtf.csrf import validate_csrf, ValidationError
from flask_login import login_required
from app import db
from app.actes import bp
from app.models import Dossier, Acte, TypeActe
from app.decorators import role_required
from datetime import datetime
from app.actes.calculators.registry import CALCULATOR_REGISTRY

# --- ROUTER DE CALCUL GÉNÉRIQUE ---

@bp.route('/types/<int:id>/bareme', methods=['GET', 'POST'])
@login_required
@role_required('NOTAIRE', 'CLERC', 'ADMIN')
def type_acte_bareme(id):
    """
    Point d'entrée principal : redirige vers la bonne route de calcul 
    en fonction du nom du TypeActe.
    """
    ta = db.session.get(TypeActe, id)
    if not ta:
        flash('Type d\'acte introuvable.', 'error')
        return redirect(url_for('actes.types_acte_index'))
    
    nom_upper = ta.nom.upper()
    
    # Mapping heuristique Nom -> Slug
    slug = None
    
    if 'SUCCESSION' in nom_upper: slug = 'succession'
    elif 'SARL' in nom_upper:
        if 'AUGM' in nom_upper: slug = 'augmentation'
        elif 'DISSOL' in nom_upper: slug = 'dissolution'
        else: slug = 'sarl'
    elif 'SCI' in nom_upper: slug = 'sci'
    elif 'SA' in nom_upper and 'CA' in nom_upper: slug = 'sa'
    elif 'ADJUD' in nom_upper: slug = 'adjudication'
    elif 'DAT' in nom_upper and 'PAIEMENT' in nom_upper: slug = 'dation'
    elif 'VENTE' in nom_upper or 'VTE' in nom_upper: slug = 'vente'
    elif 'BAIL' in nom_upper:
        if 'LOCAT' in nom_upper and 'GERAN' in nom_upper: slug = 'location_gerance'
        else: slug = 'bail'
    elif 'CES' in nom_upper and 'PARTS' in nom_upper: slug = 'cession_parts'
    elif 'DONAT' in nom_upper: slug = 'donation'
    elif 'PARTAGE' in nom_upper or 'PRTGE' in nom_upper: slug = 'partage'
    elif 'AUGM' in nom_upper: slug = 'augmentation'
    elif 'ML' == nom_upper or 'MAINLEV' in nom_upper: slug = 'mainlevee'
    elif 'HYPOT' in nom_upper or 'O. C' in nom_upper:
        if 'NANTIS' in nom_upper: slug = 'nantissement'
        else: slug = 'mortgage'
    elif 'ECHANG' in nom_upper: slug = 'echange'
    elif 'DISSOL' in nom_upper: slug = 'dissolution'
    elif 'TRANSFORM' in nom_upper: slug = 'transformation'
    elif 'FONDS' in nom_upper and 'COMMERCE' in nom_upper: slug = 'fonds_commerce'
    elif 'RGT' in nom_upper or 'COPROP' in nom_upper: slug = 'copropriete'
    elif 'MANDAT' in nom_upper and 'SEQUESTRE' in nom_upper: slug = 'mandat_sequestre'
    elif 'DEPOT' in nom_upper: slug = 'acte_depot'
    elif 'CESS' in nom_upper and 'CREANCE' in nom_upper: slug = 'cession_creances'
    elif 'NANTISSEMENT' in nom_upper: slug = 'nantissement'
    elif 'TPV' in nom_upper or 'PLUS-VALUE' in nom_upper: slug = 'tpv'
    elif 'A.O' in nom_upper or 'OCCUPER' in nom_upper: slug = 'ao'
    
    if slug and slug in CALCULATOR_REGISTRY:
        dossier_id = request.args.get('dossier_id')
        return redirect(url_for(f'actes.bareme_generic', slug=slug, type_id=id, dossier_id=dossier_id))
    
    flash(f'Le module de calcul pour {ta.nom} n\'est pas encore disponible.', 'info')
    return redirect(url_for('actes.types_acte_index'))


@bp.route('/bareme/<slug>', methods=['GET', 'POST'])
@login_required
@role_required('NOTAIRE', 'CLERC', 'ADMIN')
def bareme_generic(slug):
    """
    Route unique qui gère tous les calculs de barèmes via le registre.
    """
    config = CALCULATOR_REGISTRY.get(slug)
    if not config:
        abort(404)
        
    result = None
    params = {}
    dossiers = db.session.execute(db.select(Dossier).order_by(Dossier.numero_dossier)).scalars().all()
    
    # Pre-selected dossier from URL
    selected_dossier_id = request.args.get('dossier_id', type=int)
    
    if request.method == 'POST':
        # Manual CSRF Protection (SEC-07) - Skip in tests
        if not current_app.testing:
            try:
                validate_csrf(request.form.get('csrf_token'))
            except ValidationError:
                abort(400, "Jeton CSRF invalide.")

        action = request.form.get('action')
        
        # 1. Extraction standardisée des paramètres
        params = config['params_extractor']()
        
        # 2. Exécution du calcul
        try:
            if config.get('class'):
                result = config['class'].calculate(**params)
            elif config.get('calculator_func'):
                result = config['calculator_func'](**params)
        except Exception as e:
            flash(f"Erreur de calcul: {str(e)}", 'error')
            
        # 3. Logique de Sauvegarde (Commune à tous)
        if action == 'save' and result:
            dossier_id = request.form.get('dossier_id')
            if not dossier_id:
                flash('Veuillez sélectionner un dossier pour sauvegarder.', 'error')
            else:
                dossier = db.session.get(Dossier, int(dossier_id))
                if dossier:
                    acte = Acte(
                        dossier_id=dossier.id,
                        type_acte='NOTE DE PROVISION', # Ou utiliser config['type_acte'] comme sous-type
                        statut='BROUILLON',
                        contenu_json={
                            'type': config['type_acte'],
                            'params': params,
                            'result': result,
                            'date_simulation': datetime.utcnow().isoformat()
                        },
                        version=1
                    )
                    db.session.add(acte)
                    db.session.commit()
                    flash(f"Note de provision {config['type_acte']} sauvegardée.", 'success')
                    return redirect(url_for('dossiers.view', id=dossier.id))
    
    # 4. Rendu du template spécifique (il attend 'result', 'params', 'dossiers')
    return render_template(config['template'], result=result, params=params, dossiers=dossiers, selected_dossier_id=selected_dossier_id)

# --- ROUTES ALIAS POUR COMPATIBILITÉ (Optionnel) ---
# Si le code JS ou des liens codés en dur pointent vers /bareme/vente, 
# on peut générer ces routes dynamiquement ou les laisser mourir.
# Pour l'instant, la redirection dans `type_acte_bareme` fait le travail.
# Mais si un utilisateur a un favori sur /actes/bareme/vente , il aura une 404.
# Il vaut mieux rediriger explicitement ou utiliser `bareme_generic` pour tout.

# Pour assurer la rétrocompatibilité des URLs existantes dans les tests automatiques ou favoris:
@bp.route('/bareme/vente', endpoint='bareme_vente')
@bp.route('/bareme/sarl', endpoint='bareme_sarl')
@bp.route('/bareme/sci', endpoint='bareme_sci')
@bp.route('/bareme/sa', endpoint='bareme_sa')
@bp.route('/bareme/bail', endpoint='bareme_bail')
@bp.route('/bareme/cession_parts', endpoint='bareme_cession_parts')
@bp.route('/bareme/donation', endpoint='bareme_donation')
@bp.route('/bareme/partage', endpoint='bareme_partage')
@bp.route('/bareme/adjudication', endpoint='bareme_adjudication')
@bp.route('/bareme/augmentation', endpoint='bareme_augmentation')
@bp.route('/bareme/mainlevee', endpoint='bareme_mainlevee')
@bp.route('/bareme/mortgage', endpoint='bareme_mortgage')
@bp.route('/bareme/echange', endpoint='bareme_echange')
@bp.route('/bareme/dissolution', endpoint='bareme_dissolution')
@bp.route('/bareme/transformation', endpoint='bareme_transformation')
@bp.route('/bareme/fonds_commerce', endpoint='bareme_fonds_commerce')
@bp.route('/bareme/dation', endpoint='bareme_dation')
@bp.route('/bareme/location_gerance', endpoint='bareme_location_gerance')
@bp.route('/bareme/copropriete', endpoint='bareme_copropriete')
@bp.route('/bareme/mandat_sequestre', endpoint='bareme_mandat_sequestre')
@bp.route('/bareme/acte_depot', endpoint='bareme_acte_depot')
@bp.route('/bareme/cession_creances', endpoint='bareme_cession_creances')
@bp.route('/bareme/nantissement', endpoint='bareme_nantissement')
@bp.route('/bareme/tpv', endpoint='bareme_tpv')
@bp.route('/bareme/ao', endpoint='bareme_ao')
@bp.route('/bareme/succession', endpoint='bareme_succession')
@login_required
@role_required('NOTAIRE', 'CLERC', 'ADMIN')
def legacy_bareme_redirect():
    """
    Redirection automatique des anciennes URLs vers la nouvelle route générique.
    Ex: /bareme/vente -> /bareme/vente (géré par generic)
    Astuce: Flask associe la route à la fonction. 
    On va extraire le slug de l'URL.
    """
    slug = request.path.split('/')[-1]
    return bareme_generic(slug)

