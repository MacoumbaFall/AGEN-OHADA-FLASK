# 📂 Client Management – Enriched Profile & KYC

## Overview
The **Client** module now stores comprehensive personal and corporate data, plus a full **KYC (Know‑Your‑Customer)** workflow. All new fields are persisted in the `clients` table, exposed through the `ClientForm`, and displayed on the client list, detail view, and edit pages.

| Area | What’s new |
|------|------------|
| **Model** | Added fields for personal data, corporate data, identity documents, and KYC status/notes. |
| **Form** | `ClientForm` now includes all new fields with validation and choice lists. |
| **Routes** | `create` & `edit` use `form.populate_obj(client)` and automatically set `kyc_date_verification` when status becomes **VALIDE**. |
| **List View** (`clients/index.html`) | Shows a colour‑coded **KYC status badge** and the new fields in the table. |
| **Detail View** (`clients/view.html`) | Dedicated **KYC section** with badge, document details, and notes. |
| **Delete Guard** | Prevents deletion of a client that is linked to existing dossiers. |
| **Migrations** | Alembic migration (`13a88325ceb4_added_kyc_to_client.py`) adds columns with a default `A_VERIFIER` for `kyc_statut`. |

---

## 1. Data Model (`app/models.py`)
```python
class Client(db.Model):
    __tablename__ = 'clients'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type_client: Mapped[str] = mapped_column(String(20), nullable=False)  # PHYSIQUE / MORALE
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    prenom: Mapped[Optional[str]] = mapped_column(String(100))
    date_naissance: Mapped[Optional[datetime]] = mapped_column(Date)
    lieu_naissance: Mapped[Optional[str]] = mapped_column(String(100))
    adresse: Mapped[Optional[str]] = mapped_column(Text)
    telephone: Mapped[Optional[str]] = mapped_column(String(30))
    email: Mapped[Optional[str]] = mapped_column(String(100))
    identifiant_unique: Mapped[Optional[str]] = mapped_column(String(50))

    # ── Personne Physique ──
    profession: Mapped[Optional[str]] = mapped_column(String(100))
    nationalite: Mapped[Optional[str]] = mapped_column(String(50))
    situation_matrimoniale: Mapped[Optional[str]] = mapped_column(String(50))
    regime_matrimonial: Mapped[Optional[str]] = mapped_column(String(100))

    # ── Personne Morale ──
    forme_juridique: Mapped[Optional[str]] = mapped_column(String(50))
    capital_social: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    rccm: Mapped[Optional[str]] = mapped_column(String(100))
    ninea: Mapped[Optional[str]] = mapped_column(String(100))

    # ── KYC / Pièces d'identité ──
    type_piece_identite: Mapped[Optional[str]] = mapped_column(String(50))
    numero_piece_identite: Mapped[Optional[str]] = mapped_column(String(100))
    date_emission_piece: Mapped[Optional[datetime]] = mapped_column(Date)
    date_expiration_piece: Mapped[Optional[datetime]] = mapped_column(Date)
    autorite_emission_piece: Mapped[Optional[str]] = mapped_column(String(100))

    # ── Statut KYC ──
    kyc_statut: Mapped[str] = mapped_column(String(20), default='A_VERIFIER')
    kyc_date_verification: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    kyc_notes: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    dossier_participations = relationship('DossierParty', back_populates='client')
```
*All fields are nullable except `type_client`, `nom`, and `kyc_statut` (default `A_VERIFIER`).*

---

## 2. Form (`app/clients/forms.py`)
```python
class ClientForm(FlaskForm):
    # Basic identity
    type_client = SelectField('Type de Client',
                              choices=[('PHYSIQUE', 'Personne Physique'), ('MORALE', 'Personne Morale')],
                              validators=[DataRequired()])
    nom = StringField('Nom / Raison Sociale', validators=[DataRequired(), Length(max=100)])
    prenom = StringField('Prénom (Optionnel pour PM)', validators=[Optional(), Length(max=100)])
    date_naissance = DateField('Date de Naissance / Création', format='%Y-%m-%d', validators=[Optional()])
    lieu_naissance = StringField('Lieu de Naissance / Création', validators=[Optional(), Length(max=100)])

    # Personne Physique
    profession = StringField('Profession', validators=[Optional(), Length(max=100)])
    nationalite = StringField('Nationalité', validators=[Optional(), Length(max=50)])
    situation_matrimoniale = SelectField('Situation Matrimoniale',
                                          choices=[('', '---'), ('CÉLIBATAIRE', 'Célibataire'),
                                                   ('MARIÉ(E)', 'Marié(e)'), ('DIVORCÉ(E)', 'Divorcé(e)'),
                                                   ('VEUF/VEUVE', 'Veuf/Veuve')],
                                          validators=[Optional()])
    regime_matrimonial = StringField('Régime Matrimonial', validators=[Optional(), Length(max=100)])

    # Personne Morale
    forme_juridique = StringField('Forme Juridique', validators=[Optional(), Length(max=50)])
    capital_social = DecimalField('Capital Social', validators=[Optional()])
    rccm = StringField('Numéro RCCM', validators=[Optional(), Length(max=100)])
    ninea = StringField('NINEA', validators=[Optional(), Length(max=100)])

    # Contact
    adresse = TextAreaField('Adresse Principale', validators=[Optional()])
    telephone = StringField('Téléphone', validators=[Optional(), Length(max=30)])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=100)])
    identifiant_unique = StringField('Identifiant Unique Ancien (Optionnel)', validators=[Optional(), Length(max=50)])

    # KYC / Pièces d'identité
    type_piece_identite = SelectField('Type de Pièce',
                                      choices=[('', '---'), ('CNI', "Carte Nationale d'Identité"),
                                               ('PASSEPORT', 'Passeport'), ('CARTE_CONSULAIRE', 'Carte Consulaire'),
                                               ('EXTRAIT_RCCM', 'Extrait RCCM'), ('AUTRE', 'Autre')],
                                      validators=[Optional()])
    numero_piece_identite = StringField('Numéro de Pièce', validators=[Optional(), Length(max=100)])
    date_emission_piece = DateField("Date d'émission de la pièce", format='%Y-%m-%d', validators=[Optional()])
    date_expiration_piece = DateField("Date d'expiration de la pièce", format='%Y-%m-%d', validators=[Optional()])
    autorite_emission_piece = StringField('Autorité d\'émission', validators=[Optional(), Length(max=100)])

    # Statut KYC
    kyc_statut = SelectField('Statut KYC',
                             choices=[('A_VERIFIER', 'À vérifier'), ('VALIDE', 'Valide'),
                                      ('EXPIRE', 'Expiré'), ('REJETE', 'Rejeté')],
                             default='A_VERIFIER', validators=[DataRequired()])
    kyc_notes = TextAreaField('Notes KYC', validators=[Optional()])

    submit = SubmitField('Enregistrer le Client')
```
*All new fields are optional except the KYC status, which defaults to **À vérifier**.*

---

## 3. Routes (`app/clients/routes.py`)
```python
@bp.route('/clients/new', methods=['GET', 'POST'])
@login_required
@role_required('NOTAIRE', 'CLERC', 'SECRETAIRE', 'ADMIN')
def create():
    form = ClientForm()
    if form.validate_on_submit():
        client = Client()
        form.populate_obj(client)

        # Auto‑stamp KYC verification date when status is VALIDE
        if client.kyc_statut == 'VALIDE' and not client.kyc_date_verification:
            client.kyc_date_verification = datetime.utcnow()

        db.session.add(client)
        db.session.commit()
        flash('Client créé avec succès.', 'success')
        return redirect(url_for('clients.index'))
    return render_template('clients/form.html', title='Nouveau Client', form=form)


@bp.route('/clients/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('NOTAIRE', 'CLERC', 'ADMIN')
def edit(id):
    client = db.session.get(Client, id)
    if not client:
        flash('Client non trouvé.', 'error')
        return redirect(url_for('clients.index'))
    form = ClientForm(obj=client)
    if form.validate_on_submit():
        was_not_valide = client.kyc_statut != 'VALIDE'
        form.populate_obj(client)

        # Update verification date only when status flips to VALIDE
        if client.kyc_statut == 'VALIDE' and was_not_valide:
            client.kyc_date_verification = datetime.utcnow()

        db.session.commit()
        flash('Client modifié avec succès.', 'success')
        return redirect(url_for('clients.view', id=client.id))
    return render_template('clients/form.html', title='Modifier Client', form=form, client=client)
```
*The `populate_obj` call removes a lot of boiler‑plate field assignments.*

---

## 4. List View (`app/templates/clients/index.html`)
### New Table Columns
```html
<th class="px-3 py-3.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
    Statut KYC
</th>
```
### New Cell (after address)
```html
<td class="whitespace-nowrap px-3 py-4 text-sm">
    <span class="inline-flex rounded-full px-2 text-xs font-bold leading-5 tracking-wide
        {% if client.kyc_statut == 'VALIDE' %}bg-green-100 text-green-800
        {% elif client.kyc_statut == 'A_VERIFIER' %}bg-yellow-100 text-yellow-800
        {% else %}bg-red-100 text-red-800{% endif %}">
        {{ client.kyc_statut.replace('_', ' ') }}
    </span>
</td>
```
*The badge colour reflects the current KYC status.*

---

## 5. Detail View (`app/templates/clients/view.html`)
The **KYC section** (lines 135‑156) now shows:
- **Badge** with colour‑coding (`VALIDE` → green, `A_VERIFIER` → yellow, others → red).  
- **Document details** (type, number, issue/expiry dates, issuing authority).  
- **Notes** (optional free‑text).  
```html
<div class="bg-white shadow sm:rounded-xl overflow-hidden border border-gray-100">
    <div class="px-4 py-5 sm:px-6
        {% if client.kyc_statut == 'VALIDE' %} bg-green-50 border-b border-green-100
        {% elif client.kyc_statut == 'A_VERIFIER' %} bg-yellow-50 border-b border-yellow-100
        {% else %} bg-red-50 border-b border-red-100 {% endif %} flex justify-between items-center">
        <h3 class="text-base font-bold leading-6
            {% if client.kyc_statut == 'VALIDE' %} text-green-900
            {% elif client.kyc_statut == 'A_VERIFIER' %} text-yellow-900
            {% else %} text-red-900 {% endif %} flex items-center gap-2">
            <svg class="h-5 w-5" …>…</svg>
            Suivi KYC / Pièces Justificatives
        </h3>
        <span class="inline-flex items-center rounded-md px-2.5 py-0.5 text-xs font-black uppercase tracking-widest
            {% if client.kyc_statut == 'VALIDE' %} bg-green-200 text-green-800
            {% elif client.kyc_statut == 'A_VERIFIER' %} bg-yellow-200 text-yellow-800
            {% else %} bg-red-200 text-red-800 {% endif %}">
            {{ client.kyc_statut.replace('_', ' ') }}
        </span>
    </div>
    …
</div>
```
*If `kyc_notes` is present, a highlighted block appears below the document table.*

---

## 6. Database Migration
**File:** `migrations/versions/13a88325ceb4_added_kyc_to_client.py`
```python
def upgrade():
    with op.batch_alter_table('clients') as batch_op:
        batch_op.add_column(sa.Column('kyc_statut', sa.String(length=20), nullable=False,
                             server_default='A_VERIFIER'))
        # other new columns …
```
*Running `flask db upgrade` applies the changes without requiring manual data entry.*

---

## 7. Testing Checklist
1. **Create a client** – verify all new fields appear in the form and are saved.  
2. **List view** – confirm the KYC badge shows the correct colour and text.  
3. **Detail view** – ensure the KYC section displays all document data and notes.  
4. **Edit flow** – change `kyc_statut` to **VALIDE** and check that `kyc_date_verification` is automatically set (visible in the DB or via a debug view).  
5. **Delete guard** – try deleting a client linked to a dossier; the operation should be blocked with a flash message.  

---

## 8. Future Improvements (optional)
- **KYC alerts**: background job that scans `date_expiration_piece` and sends email reminders when a document is near expiry.  
- **Export**: CSV/Excel export of clients with KYC status for compliance reporting.  
- **Audit log**: record changes to KYC fields (who changed what and when).  

---

### How to Use This Documentation
- Place the **model**, **form**, and **route** snippets into their respective files if you need to recreate them.  
- Copy the **HTML** blocks into `clients/index.html` and `clients/view.html` at the indicated line numbers.  
- Run the migration (`flask db migrate -m "Add KYC fields"` then `flask db upgrade`).  
- Run the test checklist to verify everything works.

Feel free to adapt the wording or styling to match your project’s conventions. If you need any additional pages (e.g., a dedicated “KYC alerts” dashboard) just let me know!
