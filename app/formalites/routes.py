from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required
from app import db
from app.formalites import bp
from app.formalites.forms import FormaliteForm
from app.formalites.calculator import FormaliteCalculator, estimer_delai_formalite
from app.models import Formalite, Dossier
from sqlalchemy import select, or_
from datetime import datetime, timedelta

@bp.route('/')
@login_required
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
                         search_query=search_query)

@bp.route('/<int:id>')
@login_required
def view(id):
    """Vue détaillée d'une formalité."""
    formalite = db.session.get(Formalite, id)
    if not formalite:
        flash('Formalité introuvable.', 'error')
        return redirect(url_for('formalites.index'))
    
    # Calculer les informations supplémentaires
    delai_info = estimer_delai_formalite(formalite.type_formalite)
    
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
            type_formalite=form.type_formalite.data,
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

    if form.validate_on_submit():
        formalite.dossier_id = form.dossier.data.id
        formalite.type_formalite = form.type_formalite.data
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
def estimate_cost():
    """API endpoint pour estimer le coût d'une formalité."""
    data = request.get_json()
    type_formalite = data.get('type_formalite')
    
    if not type_formalite:
        return jsonify({'error': 'Type de formalité requis'}), 400
    
    # Paramètres optionnels selon le type
    params = {}
    if type_formalite == 'ENREGISTREMENT':
        params['montant_acte'] = float(data.get('montant_acte', 1000000))
    elif type_formalite == 'HYPOTHEQUE':
        params['montant_garanti'] = float(data.get('montant_garanti', 5000000))
    elif type_formalite == 'RCCM':
        params['type_operation'] = data.get('type_operation', 'creation')
    elif type_formalite == 'JOURNAL':
        params['nombre_lignes'] = int(data.get('nombre_lignes', 10))
    elif type_formalite == 'CADASTRE':
        params['type_operation'] = data.get('type_operation', 'immatriculation')
    
    # Calculer l'estimation
    estimation = FormaliteCalculator.calculer_formalite(type_formalite, **params)
    delai = estimer_delai_formalite(type_formalite)
    
    # Convertir les Decimal en float pour JSON
    result = {k: float(v) if hasattr(v, '__float__') else v for k, v in estimation.items()}
    result['delai_estime'] = delai
    
    return jsonify(result)
