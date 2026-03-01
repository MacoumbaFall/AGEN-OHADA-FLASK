from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.comptabilite import bp
from app.comptabilite.service import ComptabiliteService
from app.comptabilite.forms import CompteForm, RecuForm, FactureForm, RecetteForm, DepenseForm
from app.models import ComptaCompte, ComptaEcriture, Recu, Facture, TypeActe
from datetime import datetime, date
from io import BytesIO
from flask import send_file, make_response

from app.decorators import role_required

@bp.route('/')
@login_required
@role_required('COMPTABLE', 'NOTAIRE', 'ADMIN')
def index():
    """Dashboard with financial overview."""
    # Get account balances
    comptes = db.session.execute(
        db.select(ComptaCompte).filter_by(actif=True).order_by(ComptaCompte.numero_compte)
    ).scalars().all()
    
    # Calculate totals
    total_office = sum(c.get_solde() for c in comptes if c.categorie == 'OFFICE')
    total_client = sum(c.get_solde() for c in comptes if c.categorie == 'CLIENT')
    
    # Get recent receipts and invoices
    recent_recus = db.session.execute(
        db.select(Recu).order_by(Recu.date_emission.desc()).limit(5)
    ).scalars().all()
    
    recent_factures = db.session.execute(
        db.select(Facture).order_by(Facture.date_emission.desc()).limit(5)
    ).scalars().all()
    
    stats = {
        'total_office': total_office,
        'total_client': total_client,
        'nb_comptes': len(comptes),
        'nb_recus': db.session.query(Recu).count(),
        'nb_factures': db.session.query(Facture).count()
    }
    
    return render_template('comptabilite/dashboard.html',
                         stats=stats,
                         comptes=comptes,
                         recent_recus=recent_recus,
                         recent_factures=recent_factures)

@bp.route('/init-accounts', methods=['POST'])
@login_required
@role_required('ADMIN')
def init_accounts():
    """Initialize default chart of accounts."""
    try:
        ComptabiliteService.initialize_default_accounts()
        flash('Plan comptable initialisé avec succès.', 'success')
    except Exception as e:
        current_app.logger.error(f"INITIALIZATION ERROR: {str(e)}")
        flash('Une erreur est survenue lors de l\'initialisation du plan comptable.', 'error')
    return redirect(url_for('comptabilite.comptes_index'))

# ===== COMPTES (ACCOUNTS) =====

@bp.route('/comptes')
@login_required
@role_required('COMPTABLE', 'NOTAIRE', 'ADMIN')
def comptes_index():
    """List all accounts."""
    comptes = db.session.execute(
        db.select(ComptaCompte).order_by(ComptaCompte.numero_compte)
    ).scalars().all()
    
    # Group by category
    comptes_office = [c for c in comptes if c.categorie == 'OFFICE']
    comptes_client = [c for c in comptes if c.categorie == 'CLIENT']
    comptes_autres = [c for c in comptes if c.categorie not in ['OFFICE', 'CLIENT']]
    
    return render_template('comptabilite/comptes/index.html',
                         comptes_office=comptes_office,
                         comptes_client=comptes_client,
                         comptes_autres=comptes_autres)

@bp.route('/comptes/new', methods=['GET', 'POST'])
@login_required
@role_required('COMPTABLE', 'NOTAIRE', 'ADMIN')
def comptes_create():
    """Create a new account."""
    form = CompteForm()
    
    if form.validate_on_submit():
        compte = ComptaCompte(
            numero_compte=form.numero_compte.data,
            libelle=form.libelle.data,
            type_compte=form.type_compte.data,
            categorie=form.categorie.data if form.categorie.data else None,
            actif=(form.actif.data == 'True')
        )
        db.session.add(compte)
        db.session.commit()
        flash('Compte créé avec succès.', 'success')
        return redirect(url_for('comptabilite.comptes_index'))
    
    return render_template('comptabilite/comptes/form.html', form=form, title='Nouveau Compte')

# ===== RECUS (RECEIPTS) =====

@bp.route('/recus')
@login_required
@role_required('COMPTABLE', 'NOTAIRE', 'ADMIN')
def recus_index():
    """List all receipts."""
    recus = db.session.execute(
        db.select(Recu).order_by(Recu.date_emission.desc())
    ).scalars().all()
    
    total_recus = sum(r.montant for r in recus)
    
    return render_template('comptabilite/recus/index.html',
                         recus=recus,
                         total_recus=total_recus)

@bp.route('/recus/new', methods=['GET', 'POST'])
@login_required
@role_required('COMPTABLE', 'NOTAIRE', 'ADMIN')
def recus_create():
    """Create a new receipt."""
    form = RecuForm()
    
    # Handle pre-filling from simulation
    source_acte_id = request.args.get('source_acte_id', type=int)
    if source_acte_id and request.method == 'GET':
        from app.models import Acte
        acte = db.session.get(Acte, source_acte_id)
        if acte and acte.type_acte == 'NOTE DE PROVISION' and acte.contenu_json:
            res = acte.contenu_json.get('result', {})
            form.dossier.data = acte.dossier
            # Try to get the first party as client
            if acte.dossier and acte.dossier.parties:
                form.client.data = acte.dossier.parties[0].client
            form.montant.data = res.get('total_general', 0)
            form.motif.data = f"Provision pour {acte.contenu_json.get('type')} - Dossier {acte.dossier.numero_dossier}"
            form.date_emission.data = date.today()

    if form.validate_on_submit():
        try:
            recu = ComptabiliteService.create_recu(
                date_emission=form.date_emission.data,
                montant=float(form.montant.data),
                mode_paiement=form.mode_paiement.data,
                motif=form.motif.data,
                dossier_id=form.dossier.data.id if form.dossier.data else None,
                client_id=form.client.data.id if form.client.data else None,
                reference_paiement=form.reference_paiement.data,
                user_id=current_user.id
            )
            flash(f'Reçu {recu.numero_recu} créé avec succès.', 'success')
            return redirect(url_for('comptabilite.recus_view', id=recu.id))
        except Exception as e:
            flash(f'Erreur lors de la création du reçu: {str(e)}', 'error')
    
    return render_template('comptabilite/recus/form.html', form=form, title='Nouveau Reçu')

@bp.route('/recus/<int:id>')
@login_required
@role_required('COMPTABLE', 'NOTAIRE', 'ADMIN')
def recus_view(id):
    """View receipt details."""
    recu = db.session.get(Recu, id)
    if not recu:
        flash('Reçu introuvable.', 'error')
        return redirect(url_for('comptabilite.recus_index'))
    
    return render_template('comptabilite/recus/view.html', recu=recu)

@bp.route('/recus/<int:id>/download')
@login_required
@role_required('COMPTABLE', 'NOTAIRE', 'ADMIN')
def recus_download_pdf(id):
    """Download receipt as PDF."""
    recu = db.session.get(Recu, id)
    if not recu:
        flash('Reçu introuvable.', 'error')
        return redirect(url_for('comptabilite.recus_index'))
    
    from weasyprint import HTML
    
    # We render the template to a string. 
    # Note: we might need a specific template for PDF or use the view one if it's clean enough.
    # The view.html has a print-specific CSS, but for server-side PDF we might want a cleaner wrapper.
    html_content = render_template('comptabilite/recus/view.html', recu=recu, is_pdf=True)
    
    pdf_buffer = BytesIO()
    HTML(string=html_content, base_url=request.base_url).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"recu_{recu.numero_recu}.pdf",
        mimetype='application/pdf'
    )

# ===== FACTURES (INVOICES) =====

@bp.route('/factures')
@login_required
@role_required('COMPTABLE', 'NOTAIRE', 'ADMIN')
def factures_index():
    """List all invoices."""
    factures = db.session.execute(
        db.select(Facture).order_by(Facture.date_emission.desc())
    ).scalars().all()
    
    total_factures = sum(f.montant_ttc for f in factures)
    total_impayees = sum(f.montant_ttc for f in factures if f.statut == 'IMPAYEE')
    
    return render_template('comptabilite/factures/index.html',
                         factures=factures,
                         total_factures=total_factures,
                         total_impayees=total_impayees)

@bp.route('/factures/new', methods=['GET', 'POST'])
@login_required
@role_required('COMPTABLE', 'NOTAIRE', 'ADMIN')
def factures_create():
    """Create a new invoice."""
    form = FactureForm()
    
    # Handle pre-filling from simulation
    source_acte_id = request.args.get('source_acte_id', type=int)
    if source_acte_id and request.method == 'GET':
        from app.models import Acte
        acte = db.session.get(Acte, source_acte_id)
        if acte and acte.type_acte == 'NOTE DE PROVISION' and acte.contenu_json:
            res = acte.contenu_json.get('result', {})
            form.dossier.data = acte.dossier
            if acte.dossier and acte.dossier.parties:
                form.client.data = acte.dossier.parties[0].client
            form.montant_ht.data = res.get('honoraires_ht', 0)
            form.montant_tva.data = res.get('tva', 0)
            form.description.data = f"Honoraires pour {acte.contenu_json.get('type')} - Dossier {acte.dossier.numero_dossier}"
            form.date_emission.data = date.today()

    if form.validate_on_submit():
        try:
            facture = ComptabiliteService.create_facture(
                date_emission=form.date_emission.data,
                montant_ht=float(form.montant_ht.data),
                description=form.description.data,
                dossier_id=form.dossier.data.id if form.dossier.data else None,
                client_id=form.client.data.id if form.client.data else None,
                montant_tva=float(form.montant_tva.data) if form.montant_tva.data else 0,
                date_echeance=form.date_echeance.data,
                user_id=current_user.id
            )
            flash(f'Facture {facture.numero_facture} créée avec succès.', 'success')
            return redirect(url_for('comptabilite.factures_view', id=facture.id))
        except Exception as e:
            flash(f'Erreur lors de la création de la facture: {str(e)}', 'error')
    
    return render_template('comptabilite/factures/form.html', form=form, title='Nouvelle Facture')

@bp.route('/factures/<int:id>')
@login_required
@role_required('COMPTABLE', 'NOTAIRE', 'ADMIN')
def factures_view(id):
    """Affiche une facture"""
    from app.actes.services.parametres import ParametreService
    facture = db.session.get(Facture, id) # Changed from ComptaFacture to Facture to match existing model usage
    if not facture:
        flash('Facture introuvable.', 'error')
        return redirect(url_for('comptabilite.factures_index'))
    return render_template('comptabilite/factures/view.html',
                         title=f'Facture {facture.numero_facture}',
                         facture=facture,
                         p=ParametreService)

@bp.route('/factures/<int:id>/download')
@login_required
@role_required('COMPTABLE', 'NOTAIRE', 'ADMIN')
def factures_download_pdf(id):
    """Download invoice as PDF."""
    from app.actes.services.parametres import ParametreService
    facture = db.session.get(Facture, id)
    if not facture:
        flash('Facture introuvable.', 'error')
        return redirect(url_for('comptabilite.factures_index'))
    
    from weasyprint import HTML
    
    html_content = render_template('comptabilite/factures/view.html', facture=facture, is_pdf=True, p=ParametreService)
    
    pdf_buffer = BytesIO()
    HTML(string=html_content, base_url=request.base_url).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"facture_{facture.numero_facture}.pdf",
        mimetype='application/pdf'
    )

@bp.route('/recettes/new', methods=['GET', 'POST'])
@login_required
@role_required('COMPTABLE', 'NOTAIRE', 'ADMIN')
def recettes_create():
    """Create a new income entry (non-receipt)."""
    form = RecetteForm()
    if form.validate_on_submit():
        try:
            # Determine accounts
            if form.categorie_compte.data == 'OFFICE':
                 compte_tresorerie_num = ComptabiliteService.COMPTE_CAISSE_OFFICE if form.mode_paiement.data == 'ESPECES' else ComptabiliteService.COMPTE_BANQUE_OFFICE
            else:
                 compte_tresorerie_num = ComptabiliteService.COMPTE_CAISSE_CLIENT if form.mode_paiement.data == 'ESPECES' else ComptabiliteService.COMPTE_BANQUE_CLIENT
            
            compte_treso = db.session.execute(db.select(ComptaCompte).filter_by(numero_compte=compte_tresorerie_num)).scalar_one()
            compte_contrepartie = form.compte_produit.data
            
            ecriture = ComptabiliteService.create_ecriture(
                date_ecriture=form.date_operation.data,
                libelle=form.libelle.data,
                journal_code='CA' if form.mode_paiement.data == 'ESPECES' else 'BQ',
                mouvements=[
                    {'compte_id': compte_treso.id, 'debit': float(form.montant.data), 'credit': 0},
                    {'compte_id': compte_contrepartie.id, 'debit': 0, 'credit': float(form.montant.data)}
                ],
                dossier_id=form.dossier.data.id if form.dossier.data else None,
                user_id=current_user.id
            )
            ComptabiliteService.valider_ecriture(ecriture.id)
            flash('Recette enregistrée avec succès.', 'success')
            return redirect(url_for('comptabilite.index'))
        except Exception as e:
            current_app.logger.error(f"RECETTE ERROR: {str(e)}")
            flash('Une erreur est survenue lors de l\'enregistrement de la recette.', 'error')
            
    return render_template('comptabilite/recettes/form.html', form=form, title='Enregistrer une Recette')

@bp.route('/depenses/new', methods=['GET', 'POST'])
@login_required
@role_required('COMPTABLE', 'NOTAIRE', 'ADMIN')
def depenses_create():
    """Create a new expense entry."""
    form = DepenseForm()
    if form.validate_on_submit():
        try:
            # Determine accounts
            if form.categorie_compte.data == 'OFFICE':
                 compte_tresorerie_num = ComptabiliteService.COMPTE_CAISSE_OFFICE if form.mode_paiement.data == 'ESPECES' else ComptabiliteService.COMPTE_BANQUE_OFFICE
            else:
                 compte_tresorerie_num = ComptabiliteService.COMPTE_CAISSE_CLIENT if form.mode_paiement.data == 'ESPECES' else ComptabiliteService.COMPTE_BANQUE_CLIENT
            
            compte_treso = db.session.execute(db.select(ComptaCompte).filter_by(numero_compte=compte_tresorerie_num)).scalar_one()
            
            compte_charge = form.compte_charge.data
            
            if not compte_charge:
                 flash("Plan comptable incomplet ou compte non sélectionné.", 'error')
                 return render_template('comptabilite/depenses/form.html', form=form)

            ecriture = ComptabiliteService.create_ecriture(
                date_ecriture=form.date_operation.data,
                libelle=form.libelle.data,
                journal_code='CA' if form.mode_paiement.data == 'ESPECES' else 'BQ',
                mouvements=[
                    {'compte_id': compte_charge.id, 'debit': float(form.montant.data), 'credit': 0},
                    {'compte_id': compte_treso.id, 'debit': 0, 'credit': float(form.montant.data)}
                ],
                dossier_id=form.dossier.data.id if form.dossier.data else None,
                user_id=current_user.id
            )
            ComptabiliteService.valider_ecriture(ecriture.id)
            flash('Dépense enregistrée avec succès.', 'success')
            return redirect(url_for('comptabilite.index'))
        except Exception as e:
            current_app.logger.error(f"DEPENSE ERROR: {str(e)}")
            flash('Une erreur est survenue lors de l\'enregistrement de la dépense.', 'error')

    return render_template('comptabilite/depenses/form.html', form=form, title='Enregistrer une Dépense')

# ===== REPORTS =====

@bp.route('/reports/balance')
@login_required
@role_required('COMPTABLE', 'NOTAIRE', 'ADMIN')
def reports_balance():
    """Trial balance report."""
    date_fin = request.args.get('date_fin')
    if date_fin:
        date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
    else:
        date_fin = date.today()
    
    balance = ComptabiliteService.get_balance_generale(date_fin=date_fin)
    
    total_debit = sum(item['debit'] for item in balance)
    total_credit = sum(item['credit'] for item in balance)
    
    return render_template('comptabilite/reports/balance.html',
                         balance=balance,
                         total_debit=total_debit,
                         total_credit=total_credit,
                         date_fin=date_fin)

@bp.route('/reports/balance/download')
@login_required
@role_required('COMPTABLE', 'NOTAIRE', 'ADMIN')
def reports_balance_download():
    """Download trial balance as PDF."""
    date_fin = request.args.get('date_fin')
    if date_fin:
        date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
    else:
        date_fin = date.today()
    
    balance = ComptabiliteService.get_balance_generale(date_fin=date_fin)
    total_debit = sum(item['debit'] for item in balance)
    total_credit = sum(item['credit'] for item in balance)
    
    from weasyprint import HTML
    html_content = render_template('comptabilite/reports/balance.html',
                                 balance=balance,
                                 total_debit=total_debit,
                                 total_credit=total_credit,
                                 date_fin=date_fin,
                                 is_pdf=True)
    
    pdf_buffer = BytesIO()
    HTML(string=html_content, base_url=request.base_url).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"balance_generale_{date_fin}.pdf",
        mimetype='application/pdf'
    )

@bp.route('/reports/grand-livre')
@login_required
@role_required('COMPTABLE', 'NOTAIRE', 'ADMIN')
def reports_grand_livre():
    """General ledger report."""
    compte_id = request.args.get('compte_id', type=int)
    date_debut = request.args.get('date_debut')
    date_fin = request.args.get('date_fin')
    
    if date_debut:
        date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
    if date_fin:
        date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
    else:
        date_fin = date.today()
    
    mouvements = ComptabiliteService.get_grand_livre(
        compte_id=compte_id,
        date_debut=date_debut,
        date_fin=date_fin
    )
    
    comptes = db.session.execute(
        db.select(ComptaCompte).filter_by(actif=True).order_by(ComptaCompte.numero_compte)
    ).scalars().all()
    
    return render_template('comptabilite/reports/grand_livre.html',
                         mouvements=mouvements,
                         comptes=comptes,
                         compte_id=compte_id,
                         date_debut=date_debut,
                         date_fin=date_fin)

@bp.route('/reports/grand-livre/download')
@login_required
@role_required('COMPTABLE', 'NOTAIRE', 'ADMIN')
def reports_grand_livre_download():
    """Download general ledger as PDF."""
    compte_id = request.args.get('compte_id', type=int)
    date_debut = request.args.get('date_debut')
    date_fin = request.args.get('date_fin')
    
    if date_debut:
        date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
    if date_fin:
        date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
    else:
        date_fin = date.today()
    
    mouvements = ComptabiliteService.get_grand_livre(
        compte_id=compte_id,
        date_debut=date_debut,
        date_fin=date_fin
    )
    
    comptes = db.session.execute(
        db.select(ComptaCompte).filter_by(actif=True).order_by(ComptaCompte.numero_compte)
    ).scalars().all()
    
    from weasyprint import HTML
    html_content = render_template('comptabilite/reports/grand_livre.html',
                                 mouvements=mouvements,
                                 comptes=comptes,
                                 compte_id=compte_id,
                                 date_debut=date_debut,
                                 date_fin=date_fin,
                                 is_pdf=True)
    
    pdf_buffer = BytesIO()
    HTML(string=html_content, base_url=request.base_url).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    
    filename = "grand_livre"
    if compte_id:
        compte = db.session.get(ComptaCompte, compte_id)
        if compte:
            filename += f"_{compte.numero_compte}"
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"{filename}_{date_fin}.pdf",
        mimetype='application/pdf'
    )



@bp.route('/api/dossier-info/<int:id>')
@login_required
def api_dossier_info(id):
    """API endpoint to get dossier information including act type."""
    from app.models import Dossier, Acte
    dossier = db.session.get(Dossier, id)
    if not dossier:
        return jsonify({'error': 'Dossier not found'}), 404
    
    # Get the latest act type associated with this dossier
    last_acte = db.session.execute(
        db.select(Acte).filter_by(dossier_id=id).order_by(Acte.id.desc()).limit(1)
    ).scalar_one_or_none()
    
    return jsonify({
        'id': dossier.id,
        'numero_dossier': dossier.numero_dossier,
        'type_acte_id': last_acte.type_acte_id if last_acte else None
    })
