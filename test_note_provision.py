from app import create_app, db
from app.models import Acte, Dossier, Client, DossierParty, User
from datetime import datetime

app = create_app()

with app.app_context():
    # Make sure we have a user
    user = User.query.first()
    
    # Create test dossier
    client = Client(nom="Test", prenom="Note Provision", type_client="PHYSIQUE")
    db.session.add(client)
    db.session.commit()
    
    import uuid
    dossier = Dossier(numero_dossier=f"DOS-{uuid.uuid4().hex[:6].upper()}", intitule="Achat Maison")

    db.session.add(dossier)
    db.session.commit()
    
    # Add party
    party = DossierParty(dossier_id=dossier.id, client_id=client.id, role_dans_acte="Acheteur")
    db.session.add(party)
    
    # Add Note de provision
    import json
    contenu_json = {
        "type": "Vente Immobilière",
        "result": {
            "total_general": 2500000,
            "honoraires_ht": 1000000,
            "tva": 180000,
            "honoraires_details": [
                {"tranche": "0 à 5M", "taux": "5%", "base": "5000000", "montant": "250000"}
            ],
            "enregistrement": 800000,
            "taxe_tpv": 120000,
            "conservation_fonciere": 140000,
            "debours_details": {
                "timbre_fiscal": 10000,
                "frais_recherche": 25000
            },
            "frais_annexes": 150000
        }
    }
    
    acte = Acte(
        dossier_id=dossier.id,
        type_acte="NOTE DE PROVISION",
        statut="BROUILLON",
        contenu_json=contenu_json,
        created_at=datetime.utcnow()
    )
    db.session.add(acte)
    db.session.commit()
    
    print(f"Note de provision créée avec l'ID: {acte.id}")
