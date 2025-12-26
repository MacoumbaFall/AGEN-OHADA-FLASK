from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.dossiers import bp
from app.dossiers.forms import DossierForm, DossierPartyForm
from app.models import Dossier, User, Client, DossierParty
from sqlalchemy import select, or_
from datetime import datetime

from app.decorators import role_required

@bp.route('/')
@login_required
@role_required('NOTAIRE', 'CLERC', 'ADMIN')
def index():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '', type=str)

    query = select(Dossier).order_by(Dossier.created_at.desc())
    
    if q:
        search_term = f"%{q}%"
        query = query.where(
            or_(
                Dossier.numero_dossier.ilike(search_term),
                Dossier.intitule.ilike(search_term)
            )
        )
        
    pagination = db.paginate(query, page=page, per_page=10, error_out=False)
    dossiers = pagination.items

    return render_template('dossiers/index.html', dossiers=dossiers, pagination=pagination, q=q)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
@role_required('NOTAIRE', 'CLERC', 'ADMIN')
def create():
    form = DossierForm()
    # Populate users for responsible selection
    form.responsable_id.choices = [(u.id, u.username) for u in db.session.scalars(select(User)).all()]
    if request.method == 'GET' and not form.responsable_id.data:
        form.responsable_id.data = current_user.id
        
    if form.validate_on_submit():
        dossier = Dossier(
            numero_dossier=form.numero_dossier.data,
            intitule=form.intitule.data,
            type_dossier=form.type_dossier.data,
            statut=form.statut.data,
            date_ouverture=form.date_ouverture.data or datetime.utcnow(),
            responsable_id=form.responsable_id.data
        )
        db.session.add(dossier)
        db.session.commit()
        flash('Dossier créé avec succès.', 'success')
        return redirect(url_for('dossiers.view', id=dossier.id))
    return render_template('dossiers/form.html', title='Nouveau Dossier', form=form)

@bp.route('/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('NOTAIRE', 'CLERC', 'ADMIN')
def view(id):
    dossier = db.session.get(Dossier, id)
    if not dossier:
        flash('Dossier non trouvé.', 'error')
        return redirect(url_for('dossiers.index'))
    
    form = DossierPartyForm()
    # Populate client choices
    form.client_id.choices = [(c.id, f"{c.nom} {c.prenom or ''}") for c in db.session.scalars(select(Client).order_by(Client.nom)).all()]

    if form.validate_on_submit():
        existing_party = db.session.scalar(
            select(DossierParty).where(
                DossierParty.dossier_id == dossier.id,
                DossierParty.client_id == form.client_id.data
            )
        )
        if existing_party:
            flash('Ce client est déjà lié à ce dossier.', 'warning')
        else:
            party = DossierParty(
                dossier_id=dossier.id,
                client_id=form.client_id.data,
                role_dans_acte=form.role_dans_acte.data
            )
            db.session.add(party)
            db.session.commit()
            flash('Partie ajoutée au dossier.', 'success')
        return redirect(url_for('dossiers.view', id=id))

    return render_template('dossiers/view.html', dossier=dossier, form=form)

@bp.route('/<int:dossier_id>/remove_party/<int:client_id>', methods=['POST'])
@login_required
@role_required('NOTAIRE', 'CLERC', 'ADMIN')
def remove_party(dossier_id, client_id):
    party = db.session.scalar(
        select(DossierParty).where(
            DossierParty.dossier_id == dossier_id,
            DossierParty.client_id == client_id
        )
    )
    if party:
        db.session.delete(party)
        db.session.commit()
        flash('Partie retirée du dossier.', 'success')
    else:
        flash('Partie introuvable.', 'error')
    return redirect(url_for('dossiers.view', id=dossier_id))

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('NOTAIRE', 'CLERC', 'ADMIN')
def edit(id):
    dossier = db.session.get(Dossier, id)
    if not dossier:
        flash('Dossier non trouvé.', 'error')
        return redirect(url_for('dossiers.index'))
    
    form = DossierForm(obj=dossier)
    form.responsable_id.choices = [(u.id, u.username) for u in db.session.scalars(select(User)).all()]

    if form.validate_on_submit():
        dossier.numero_dossier = form.numero_dossier.data
        dossier.intitule = form.intitule.data
        dossier.type_dossier = form.type_dossier.data
        dossier.statut = form.statut.data
        dossier.date_ouverture = form.date_ouverture.data
        dossier.responsable_id = form.responsable_id.data
        
        db.session.commit()
        flash('Dossier mis à jour.', 'success')
        return redirect(url_for('dossiers.view', id=dossier.id))
        
    return render_template('dossiers/form.html', title='Modifier Dossier', form=form, dossier=dossier)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@role_required('ADMIN', 'NOTAIRE')
def delete(id):
    dossier = db.session.get(Dossier, id)
    if not dossier:
        flash('Dossier non trouvé.', 'error')
        return redirect(url_for('dossiers.index'))
    
    db.session.delete(dossier)
    db.session.commit()
    flash('Dossier supprimé avec succès.', 'success')
    return redirect(url_for('dossiers.index'))

@bp.route('/archives')
@login_required
@role_required('NOTAIRE', 'CLERC', 'ADMIN')
def archives():
    page = request.args.get('page', 1, type=int)
    num = request.args.get('num', '', type=str)
    title = request.args.get('title', '', type=str)
    client_name = request.args.get('client', '', type=str)
    type_dos = request.args.get('type', '', type=str)

    query = select(Dossier).where(Dossier.statut == 'ARCHIVE').order_by(Dossier.created_at.desc())
    
    if num:
        query = query.where(Dossier.numero_dossier.ilike(f"%{num}%"))
    if title:
        query = query.where(Dossier.intitule.ilike(f"%{title}%"))
    if type_dos:
        query = query.where(Dossier.type_dossier == type_dos)
    if client_name:
        # Join with parties and clients to search by client name
        query = query.join(Dossier.parties).join(DossierParty.client).where(
            or_(
                Client.nom.ilike(f"%{client_name}%"),
                Client.prenom.ilike(f"%{client_name}%")
            )
        )
        
    pagination = db.paginate(query, page=page, per_page=10, error_out=False)
    dossiers = pagination.items

    return render_template('dossiers/archives.html', dossiers=dossiers, pagination=pagination, 
                           num=num, title=title, client=client_name, type_dos=type_dos)
