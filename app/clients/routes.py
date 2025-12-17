from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required
from app import db
from app.clients import bp
from app.clients.forms import ClientForm
from app.models import Client
from sqlalchemy import select, or_

@bp.route('/clients')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '', type=str)
    
    query = select(Client).order_by(Client.nom)
    
    if q:
        search_term = f"%{q}%"
        query = query.where(
            or_(
                Client.nom.ilike(search_term),
                Client.prenom.ilike(search_term),
                Client.email.ilike(search_term)
            )
        )
        
    pagination = db.paginate(query, page=page, per_page=10, error_out=False)
    clients = pagination.items
    
    return render_template('clients/index.html', clients=clients, pagination=pagination, q=q)

@bp.route('/clients/new', methods=['GET', 'POST'])
@login_required
def create():
    form = ClientForm()
    if form.validate_on_submit():
        client = Client(
            type_client=form.type_client.data,
            nom=form.nom.data,
            prenom=form.prenom.data,
            date_naissance=form.date_naissance.data,
            lieu_naissance=form.lieu_naissance.data,
            adresse=form.adresse.data,
            telephone=form.telephone.data,
            email=form.email.data,
            identifiant_unique=form.identifiant_unique.data
        )
        db.session.add(client)
        db.session.commit()
        flash('Client créé avec succès.', 'success')
        return redirect(url_for('clients.index'))
    return render_template('clients/form.html', title='Nouveau Client', form=form)

@bp.route('/clients/<int:id>')
@login_required
def view(id):
    client = db.session.get(Client, id)
    if not client:
        flash('Client non trouvé.', 'error')
        return redirect(url_for('clients.index'))
    return render_template('clients/view.html', client=client)

@bp.route('/clients/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    client = db.session.get(Client, id)
    if not client:
        flash('Client non trouvé.', 'error')
        return redirect(url_for('clients.index'))
    form = ClientForm(obj=client)
    if form.validate_on_submit():
        client.type_client = form.type_client.data
        client.nom = form.nom.data
        client.prenom = form.prenom.data
        client.date_naissance = form.date_naissance.data
        client.lieu_naissance = form.lieu_naissance.data
        client.adresse = form.adresse.data
        client.telephone = form.telephone.data
        client.email = form.email.data
        client.identifiant_unique = form.identifiant_unique.data
        db.session.commit()
        flash('Client modifié avec succès.', 'success')
        return redirect(url_for('clients.view', id=client.id))
    return render_template('clients/form.html', title='Modifier Client', form=form, client=client)

@bp.route('/clients/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    client = db.session.get(Client, id)
    if not client:
        flash('Client non trouvé.', 'error')
        return redirect(url_for('clients.index'))
    
    if client.dossier_participations:
         flash('Impossible de supprimer ce client car il est lié à des dossiers existants.', 'error')
         return redirect(url_for('clients.view', id=id))

    db.session.delete(client)
    db.session.commit()
    flash('Client supprimé avec succès.', 'success')
    return redirect(url_for('clients.index'))
