from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required
from app import db
from app.formalites import bp
from app.formalites.forms import FormaliteForm, TypeFormaliteForm
from app.formalites.calculator import FormaliteCalculator, estimer_delai_formalite
from app.models import Formalite, Dossier, TypeFormalite
from sqlalchemy import select, or_
from datetime import datetime, timedelta

from app.decorators import role_required

@bp.route('/')
@login_required
@role_required('CLERC', 'SECRETAIRE', 'ADMIN', 'NOTAIRE')
def index():
    """Liste des formalités avec filtrage et recherche."""
    # Récupérer les paramètres de filtrage
    statut_filter = request.args.get('statut', '')
    type_filter = request.args.get('type', '')
    search_query = request.args.get('q', '')
    
    # Construire la requête de base
    query = db.select(Formalite)
    
    # Appliquer les filtres
    if statut_filter:
        query = query.filter(Formalite.statut == statut_filter)
    
    if type_filter:
        try:
            type_id = int(type_filter)
            query = query.filter(Formalite.type_id == type_id)
        except ValueError:
            query = query.filter(Formalite.type_formalite == type_filter)
    
    if search_query:
        query = query.join(Dossier).filter(
            or_(
                Dossier.numero_dossier.ilike(f'%{search_query}%'),
                Dossier.intitule.ilike(f'%{search_query}%'),
                Formalite.reference_externe.ilike(f'%{search_query}%')
            )
        )
    
    # Ordonner par date de dépôt (les plus récentes en premier)
    query = query.order_by(Formalite.date_depot.desc().nullslast(), Formalite.id.desc())
    
    formalites = db.session.scalars(query).all()
    types_formalite = db.session.scalars(db.select(TypeFormalite).order_by(TypeFormalite.nom)).all()
    
    # Calculer les statistiques
    stats = {
        'total': len(formalites),
        'a_faire': sum(1 for f in formalites if f.statut == 'A_FAIRE'),
        'en_cours': sum(1 for f in formalites if f.statut == 'EN_COURS'),
        'termine': sum(1 for f in formalites if f.statut == 'TERMINE'),
        'cout_total_estime': sum(f.cout_estime or 0 for f in formalites),
        'cout_total_reel': sum(f.cout_reel or 0 for f in formalites)
    }
    
    return render_template('formalites/index.html', 
                         formalites=formalites, 
                         stats=stats,
                         statut_filter=statut_filter,
                         type_filter=type_filter,
                         search_query=search_query,
                         types_formalite=types_formalite)

@bp.route('/types')
@login_required
@role_required('ADMIN', 'NOTAIRE')
def types_index():
    """Liste des types de formalités."""
    types = db.session.scalars(db.select(TypeFormalite).order_by(TypeFormalite.nom)).all()
    return render_template('formalites/types/index.html', types=types)

@bp.route('/types/new', methods=['GET', 'POST'])
@login_required
@role_required('ADMIN', 'NOTAIRE')
def type_create():
    """Créer un nouveau type de formalité."""
    form = TypeFormaliteForm()
    if form.validate_on_submit():
        type_formalite = TypeFormalite(
            nom=form.nom.data,
            description=form.description.data,
            cout_base=form.cout_base.data,
            delai_moyen=int(form.delai_moyen.data) if form.delai_moyen.data else None
        )
        db.session.add(type_formalite)
        db.session.commit()
        flash('Type de formalité créé avec succès.', 'success')
        return redirect(url_for('formalites.types_index'))
    return render_template('formalites/types/form.html', form=form, title='Nouveau Type de Formalité')

@bp.route('/types/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('ADMIN', 'NOTAIRE')
def type_edit(id):
    """Modifier un type de formalité."""
    type_formalite = db.session.get(TypeFormalite, id)
    if not type_formalite:
        flash('Type de formalité introuvable.', 'error')
        return redirect(url_for('formalites.types_index'))
    
    form = TypeFormaliteForm(obj=type_formalite)
    if form.validate_on_submit():
        type_formalite.nom = form.nom.data
        type_formalite.description = form.description.data
        type_formalite.cout_base = form.cout_base.data
        type_formalite.delai_moyen = int(form.delai_moyen.data) if form.delai_moyen.data else None
        db.session.commit()
        flash('Type de formalité mis à jour.', 'success')
        return redirect(url_for('formalites.types_index'))
    return render_template('formalites/types/form.html', form=form, title='Modifier Type de Formalité', type=type_formalite)

@bp.route('/<int:id>')
@login_required
@role_required('CLERC', 'SECRETAIRE', 'ADMIN', 'NOTAIRE')
def view(id):
    """Vue détaillée d'une formalité."""
    formalite = db.session.get(Formalite, id)
    if not formalite:
        flash('Formalité introuvable.', 'error')
        return redirect(url_for('formalites.index'))
    
    # Calculer les informations supplémentaires
    delai_info = estimer_delai_formalite(formalite.type_relation.nom if formalite.type_relation else formalite.type_formalite)
    
    # Calculer le délai écoulé si déposé
    jours_ecoules = None
    if formalite.date_depot:
        jours_ecoules = (datetime.now().date() - formalite.date_depot).days
    
    return render_template('formalites/view.html', 
                         formalite=formalite,
                         delai_info=delai_info,
                         jours_ecoules=jours_ecoules)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
@role_required('CLERC', 'SECRETAIRE', 'ADMIN', 'NOTAIRE')
def create():
    """Créer une nouvelle formalité."""
    form = FormaliteForm()
    
    # Pre-select dossier if passed in query string
    dossier_id = request.args.get('dossier_id')
    if dossier_id:
        dossier = db.session.get(Dossier, dossier_id)
        if dossier:
            form.dossier.data = dossier

    if form.validate_on_submit():
        formalite = Formalite(
            dossier_id=form.dossier.data.id,
            type_id=form.type_id.data.id,
            type_formalite=form.type_id.data.nom, # Sync fallback field
            statut=form.statut.data,
            date_depot=form.date_depot.data,
            date_retour=form.date_retour.data,
            cout_estime=form.cout_estime.data,
            cout_reel=form.cout_reel.data,
            reference_externe=form.reference_externe.data
        )
        db.session.add(formalite)
        db.session.commit()
        flash('Formalité créée avec succès.', 'success')
        return redirect(url_for('formalites.view', id=formalite.id))
    
    return render_template('formalites/form.html', form=form, title='Nouvelle Formalité')

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('CLERC', 'ADMIN', 'NOTAIRE')
def edit(id):
    """Modifier une formalité existante."""
    formalite = db.session.get(Formalite, id)
    if not formalite:
        flash('Formalité introuvable.', 'error')
        return redirect(url_for('formalites.index'))
    
    form = FormaliteForm(obj=formalite)
    
    # Correctly map the relationship back to the form field
    if request.method == 'GET':
        form.dossier.data = formalite.dossier
        if formalite.type_relation:
            form.type_id.data = formalite.type_relation

    if form.validate_on_submit():
        formalite.dossier_id = form.dossier.data.id
        formalite.type_id = form.type_id.data.id
        formalite.type_formalite = form.type_id.data.nom # Sync fallback field
        formalite.statut = form.statut.data
        formalite.date_depot = form.date_depot.data
        formalite.date_retour = form.date_retour.data
        formalite.cout_estime = form.cout_estime.data
        formalite.cout_reel = form.cout_reel.data
        formalite.reference_externe = form.reference_externe.data
        
        db.session.commit()
        flash('Formalité mise à jour.', 'success')
        return redirect(url_for('formalites.view', id=formalite.id))
    
    return render_template('formalites/form.html', form=form, title='Modifier Formalité', formalite=formalite)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@role_required('ADMIN', 'NOTAIRE')
def delete(id):
    """Supprimer une formalité."""
    formalite = db.session.get(Formalite, id)
    if formalite:
        db.session.delete(formalite)
        db.session.commit()
        flash('Formalité supprimée.', 'success')
    return redirect(url_for('formalites.index'))

@bp.route('/<int:id>/update-status', methods=['POST'])
@login_required
@role_required('CLERC', 'SECRETAIRE', 'ADMIN', 'NOTAIRE')
def update_status(id):
    """Mettre à jour le statut d'une formalité."""
    formalite = db.session.get(Formalite, id)
    if not formalite:
        return jsonify({'error': 'Formalité introuvable'}), 404
    
    new_status = request.form.get('statut')
    if new_status in ['A_FAIRE', 'EN_COURS', 'DEPOSE', 'TERMINE', 'ANNULE']:
        formalite.statut = new_status
        
        # Mettre à jour automatiquement les dates selon le statut
        if new_status == 'DEPOSE' and not formalite.date_depot:
            formalite.date_depot = datetime.now().date()
        elif new_status == 'TERMINE' and not formalite.date_retour:
            formalite.date_retour = datetime.now().date()
        
        db.session.commit()
        flash(f'Statut mis à jour: {new_status}', 'success')
    else:
        flash('Statut invalide.', 'error')
    
    return redirect(url_for('formalites.view', id=id))

@bp.route('/api/estimate-cost', methods=['POST'])
@login_required
@role_required('CLERC', 'SECRETAIRE', 'ADMIN', 'NOTAIRE')
def estimate_cost():
    """API endpoint pour estimer le coût d'une formalité."""
    data = request.get_json()
    type_id = data.get('type_id')
    type_name = data.get('type_formalite')
    
    type_formalite_obj = None
    if type_id:
        type_formalite_obj = db.session.get(TypeFormalite, type_id)
    elif type_name:
        type_formalite_obj = db.session.scalar(db.select(TypeFormalite).where(TypeFormalite.nom == type_name))
        
    if not type_formalite_obj and not type_name:
        return jsonify({'error': 'Type de formalité requis'}), 400
    
    # Nom du type pour le calculateur (soit celui de l'objet, soit le texte brut)
    final_type_name = type_formalite_obj.nom if type_formalite_obj else type_name
    
    # Paramètres par défaut ou spécifiques
    params = {}
    if type_formalite_obj and type_formalite_obj.cout_base:
        params['cout_base'] = type_formalite_obj.cout_base
        
    if final_type_name == 'ENREGISTREMENT' or final_type_name == 'ENREGISTREMENT IMPÔTS':
        params['montant_acte'] = float(data.get('montant_acte', 1000000))
    elif final_type_name == 'HYPOTHEQUE' or final_type_name == 'INSCRIPTION HYPOTHÉCAIRE':
        params['montant_garanti'] = float(data.get('montant_garanti', 5000000))
    elif final_type_name == 'RCCM' or final_type_name == 'DÉPÔT RCCM':
        params['type_operation'] = data.get('type_operation', 'creation')
    elif final_type_name == 'JOURNAL' or final_type_name == 'PUBLICATION JOURNAL OFFICIEL':
        params['nombre_lignes'] = int(data.get('nombre_lignes', 10))
    elif final_type_name == 'CADASTRE' or final_type_name == 'FORMALITÉS CADASTRALES':
        params['type_operation'] = data.get('type_operation', 'immatriculation')
    
    # Calculer l'estimation via le calculateur (qui gère la logique complexe ou le fallback)
    estimation = FormaliteCalculator.calculer_formalite(final_type_name, **params)
    
    # Détermination du délai
    if type_formalite_obj and type_formalite_obj.delai_moyen:
        delai = {
            'jours': type_formalite_obj.delai_moyen,
            'description': f'Délai moyen configuré pour {type_formalite_obj.nom}'
        }
    else:
        delai = estimer_delai_formalite(final_type_name)
    
    # Convertir les Decimal en float pour JSON
    result = {k: float(v) if hasattr(v, '__float__') else v for k, v in estimation.items()}
    result['delai_estime'] = delai
    
    return jsonify(result)
