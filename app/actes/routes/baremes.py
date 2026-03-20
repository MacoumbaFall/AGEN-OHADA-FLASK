from flask import render_template, flash, redirect, url_for, request, current_app, abort, jsonify
from flask_wtf.csrf import validate_csrf, ValidationError
from flask_login import login_required, current_user
from app import db
from app.actes import bp
from app.models import Dossier, Acte, TypeActe, BaremeModele, BaremeVariable, BaremeLigneCalcul
from app.decorators import role_required
from datetime import datetime
import json
from app.actes.calculators.registry import CALCULATOR_REGISTRY
from app.actes.calculators.dynamic_engine import DynamicCalculatorEngine

# --- ROUTER DE CALCUL MÉTIER ---

@bp.route('/types/<int:id>/bareme', methods=['GET', 'POST'])
@login_required
@role_required('NOTAIRE', 'CLERC', 'ADMIN')
def type_acte_bareme(id):
    """
    Point d'entrée principal : redirige vers le barème dynamique s'il existe,
    sinon vers l'ancien moteur slug-based.
    """
    ta = db.session.get(TypeActe, id)
    if not ta:
        flash('Type d\'acte introuvable.', 'error')
        return redirect(url_for('actes.types_acte_index'))
    
    # 1. Priorité au Barème Dynamique (Boutique No-Code)
    bareme_dyn = BaremeModele.query.filter_by(code=ta.nom.upper(), is_active=True).first()
    if not bareme_dyn:
        # Fallback sur recherche par ID ou nom partiel
        bareme_dyn = BaremeModele.query.filter_by(type_acte_id=id, is_active=True).first()

    if bareme_dyn:
        dossier_id = request.args.get('dossier_id')
        return redirect(url_for('actes.bareme_dynamique_view', code=bareme_dyn.code, dossier_id=dossier_id))

    # 2. Fallback sur les anciens calculateurs hardcodés
    nom_upper = ta.nom.upper()
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


# --- MOTEUR DYNAMIQUE (USER VIEW) ---

@bp.route('/bareme-dynamique/<code>')
@login_required
def bareme_dynamique_view(code):
    bareme = BaremeModele.query.filter_by(code=code).first_or_404()
    dossiers = Dossier.query.filter_by(statut='OUVERT').order_by(Dossier.numero_dossier.desc()).limit(50).all()
    selected_dossier_id = request.args.get('dossier_id', type=int)
    return render_template('actes/admin/bareme_dynamic.html', bareme=bareme, dossiers=dossiers, selected_dossier_id=selected_dossier_id)

@bp.route('/bareme-dynamique/<code>/calc', methods=['POST'])
@login_required
def bareme_dynamique_calc(code):
    inputs = request.json
    try:
        result = DynamicCalculatorEngine.calculate(code, inputs)
        return jsonify(result)
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@bp.route('/bareme-dynamique/<code>/save', methods=['POST'])
@login_required
def bareme_dynamique_save(code):
    data = request.json
    dossier_id = data.get('dossier_id')
    result = data.get('result')
    inputs = data.get('inputs')
    
    dossier = db.session.get(Dossier, dossier_id)
    if not dossier:
        return jsonify({'message': 'Dossier introuvable'}), 404
        
    acte = Acte(
        dossier_id=dossier.id,
        type_acte='NOTE DE PROVISION DYNAMIQUE',
        statut='BROUILLON',
        contenu_json={
            'bareme_code': code,
            'inputs': inputs,
            'result': result,
            'date_simulation': datetime.utcnow().isoformat()
        }
    )
    db.session.add(acte)
    db.session.commit()
    return jsonify({'redirect': url_for('dossiers.view', id=dossier.id)})


# --- ADMINISTRATION DES BARÈMES (CRUD) ---

@bp.route('/admin/baremes')
@login_required
@role_required('ADMIN')
def bareme_admin_index():
    baremes = BaremeModele.query.order_by(BaremeModele.code).all()
    return render_template('actes/admin/baremes_index.html', baremes=baremes)

@bp.route('/admin/baremes/new', methods=['GET', 'POST'])
@login_required
@role_required('ADMIN')
def bareme_admin_new():
    if request.method == 'POST':
        b = BaremeModele(
            code=request.form.get('code', '').upper(),
            nom=request.form.get('nom'),
            description=request.form.get('description'),
            is_active='is_active' in request.form
        )
        db.session.add(b)
        db.session.commit()
        return redirect(url_for('actes.bareme_admin_builder', id=b.id))
    return render_template('actes/admin/bareme_form.html', bareme=None)

@bp.route('/admin/baremes/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('ADMIN')
def bareme_admin_edit(id):
    b = db.session.get(BaremeModele, id)
    if request.method == 'POST':
        b.code = request.form.get('code', '').upper()
        b.nom = request.form.get('nom')
        b.description = request.form.get('description')
        b.is_active = 'is_active' in request.form
        db.session.commit()
        return redirect(url_for('actes.bareme_admin_index'))
    return render_template('actes/admin/bareme_form.html', bareme=b)

@bp.route('/admin/baremes/<int:id>/builder')
@login_required
@role_required('ADMIN')
def bareme_admin_builder(id):
    b = db.session.get(BaremeModele, id)
    # Préparer le JSON pour Alpine.js
    vars_json = []
    for v in b.variables:
        vars_json.append({
            'id': v.id, 'code': v.code, 'label': v.label, 'type_champ': v.type_champ, 
            'choix_json': v.choix_json, 'valeur_defaut': v.valeur_defaut, 'requis': v.requis, 'ordre': v.ordre
        })
    lines_json = []
    for l in b.lignes:
        lines_json.append({
            'id': l.id, 'ordre': l.ordre, 'code': l.code, 'libelle': l.libelle, 'type_ligne': l.type_ligne,
            'condition_affichage': l.condition_affichage, 'formule_ou_montant': l.formule_ou_montant,
            'tranches_json': l.tranches_json, 'soumis_tva': l.soumis_tva
        })
    return render_template('actes/admin/bareme_builder.html', bareme=b, variables_json=json.dumps(vars_json), lines_json=json.dumps(lines_json))

@bp.route('/admin/baremes/<int:id>/save', methods=['POST'])
@login_required
@role_required('ADMIN')
def bareme_admin_save(id):
    b = db.session.get(BaremeModele, id)
    data = request.json
    
    # 1. Sync Variables
    # Clean old ones (simple approach for now)
    BaremeVariable.query.filter_by(bareme_id=id).delete()
    for v_data in data.get('variables', []):
        choix = None
        if v_data.get('type_champ') == 'CHOIX' and v_data.get('choix_str'):
            choix = [c.strip() for c in v_data['choix_str'].split(',')]
            
        v = BaremeVariable(
            bareme_id=id,
            code=v_data.get('code'),
            label=v_data.get('label'),
            type_champ=v_data.get('type_champ'),
            choix_json=choix,
            valeur_defaut=str(v_data.get('valeur_defaut', '')),
            requis=bool(v_data.get('requis', True)),
            ordre=int(v_data.get('ordre', 0))
        )
        db.session.add(v)
        
    # 2. Sync Lines
    BaremeLigneCalcul.query.filter_by(bareme_id=id).delete()
    for l_data in data.get('lines', []):
        l = BaremeLigneCalcul(
            bareme_id=id,
            ordre=int(l_data.get('ordre', 0)),
            code=l_data.get('code', '').upper(),
            libelle=l_data.get('libelle'),
            type_ligne=l_data.get('type_ligne'),
            condition_affichage=l_data.get('condition_affichage'),
            formule_ou_montant=str(l_data.get('formule_ou_montant', '')),
            tranches_json=l_data.get('tranches_json'),
            soumis_tva=bool(l_data.get('soumis_tva', False))
        )
        db.session.add(l)
        
    db.session.commit()
    return jsonify({'status': 'ok'})


# --- LEGACY SLUG ROUTER (Maintien des anciennes routes) ---

@bp.route('/bareme/<slug>', methods=['GET', 'POST'])
@login_required
@role_required('NOTAIRE', 'CLERC', 'ADMIN')
def bareme_generic(slug):
    """
    Reste identique pour les calculateurs statiques non encore migrés.
    """
    config = CALCULATOR_REGISTRY.get(slug)
    if not config:
        abort(404)
        
    result = None
    params = {}
    dossiers = db.session.execute(db.select(Dossier).order_by(Dossier.numero_dossier.desc())).scalars().all()
    selected_dossier_id = request.args.get('dossier_id', type=int)
    
    if request.method == 'POST':
        if not current_app.testing:
            try: validate_csrf(request.form.get('csrf_token'))
            except ValidationError: abort(400, "Jeton CSRF invalide.")

        action = request.form.get('action')
        params = config['params_extractor']()
        
        try:
            if config.get('class'): result = config['class'].calculate(**params)
            elif config.get('calculator_func'): result = config['calculator_func'](**params)
        except Exception as e: flash(f"Erreur de calcul: {str(e)}", 'error')
            
        if action == 'save' and result:
            dossier_id = request.form.get('dossier_id')
            if not dossier_id: flash('Veuillez sélectionner un dossier pour sauvegarder.', 'error')
            else:
                dossier = db.session.get(Dossier, int(dossier_id))
                if dossier:
                    acte = Acte(
                        dossier_id=dossier.id,
                        type_acte='NOTE DE PROVISION',
                        statut='BROUILLON',
                        contenu_json={'type': config['type_acte'], 'params': params, 'result': result, 'date_simulation': datetime.utcnow().isoformat()},
                        version=1
                    )
                    db.session.add(acte)
                    db.session.commit()
                    flash(f"Note de provision {config['type_acte']} sauvegardée.", 'success')
                    return redirect(url_for('dossiers.view', id=dossier.id))
    
    return render_template(config['template'], result=result, params=params, dossiers=dossiers, selected_dossier_id=selected_dossier_id)

@bp.route('/bareme/vente', endpoint='bareme_vente')
@bp.route('/bareme/sarl', endpoint='bareme_sarl')
@bp.route('/bareme/sci', endpoint='bareme_sci')
# ... on pourrait ajouter les autres, mais bareme_generic est suffisant si appelé via type_acte_bareme
def legacy_bareme_redirect_bis():
    slug = request.path.split('/')[-1]
    return bareme_generic(slug)


