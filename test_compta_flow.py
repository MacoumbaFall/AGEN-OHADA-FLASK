from app import create_app, db
from app.comptabilite.service import ComptabiliteService
from app.models import ComptaCompte, Client, Dossier, User
from datetime import date
from sqlalchemy.orm import class_mapper

app = create_app()

with app.app_context():
    # 1. Initialize default accounts
    print("Initialisation des comptes...")
    ComptabiliteService.initialize_default_accounts()
    print("Comptes existants:")
    comptes = ComptaCompte.query.filter_by(actif=True).order_by(ComptaCompte.numero_compte).all()
    for c in comptes:
        print(f" - {c.numero_compte}: {c.libelle}")
        
    # Create test user if not exists
    user = User.query.first()
    if not user:
        user = User(username="test", email="test@test.com", password_hash="test", role="NOTAIRE")
        db.session.add(user)
        db.session.commit()
    
    # 2. Test creation of invoice
    print("\n\nCréation d'une facture...")
    try:
        facture = ComptabiliteService.create_facture(
            date_emission=date.today(),
            montant_ht=100000,
            montant_tva=18000,
            description="Frais d'acte de vente",
            user_id=user.id
        )
        print(f"Facture créée: {facture.numero_facture}, TTC: {facture.montant_ttc}")
        if facture.ecriture_id:
            print(f"ID Écriture comptable (Vente): {facture.ecriture_id}")
            # check the entries for this invoice
            from app.models import ComptaMouvement, ComptaEcriture
            mouvements = db.session.query(ComptaMouvement).filter_by(ecriture_id=facture.ecriture_id).all()
            for m in mouvements:
                compte = db.session.get(ComptaCompte, m.compte_id)
                print(f"  [{compte.numero_compte}] Debit: {m.debit}, Credit: {m.credit}")
        else:
            print("Erreur: L'écriture de la facture n'a pas été créée !")
            
    except Exception as e:
        print(f"Erreur facture: {e}")

    # 3. Test creation of abstract recipe
    print("\n\nCréation d'une recette...")
    try:
        compte_banque = ComptaCompte.query.filter_by(numero_compte='512-OFFICE').first()
        compte_honoraires = ComptaCompte.query.filter_by(numero_compte='706').first()
        
        mouvements = [
            {'compte_id': compte_banque.id, 'debit': 118000, 'credit': 0},
            {'compte_id': compte_honoraires.id, 'debit': 0, 'credit': 118000} # for testing, simple
        ]
        
        ecriture = ComptabiliteService.create_ecriture(
            date_ecriture=date.today(),
            libelle="Recette pour honoraires divers",
            journal_code='BQ',
            mouvements=mouvements,
            user_id=user.id
        )
        ComptabiliteService.valider_ecriture(ecriture.id)
        
        print(f"Recette créée avec succès, ID Ecriture: {ecriture.id}")
        mouvements = db.session.query(ComptaMouvement).filter_by(ecriture_id=ecriture.id).all()
        for m in mouvements:
            compte = db.session.get(ComptaCompte, m.compte_id)
            print(f"  [{compte.numero_compte}] Debit: {m.debit}, Credit: {m.credit}")
            
    except Exception as e:
        print(f"Erreur recette: {e}")


    # 4. Check Balance Générale
    print("\n\nBalance Générale:")
    balance = ComptabiliteService.get_balance_generale()
    
    total_debit = 0
    total_credit = 0
    
    for item in balance:
        print(f"{item['numero_compte']:<12} {item['libelle'][:30]:<30} | Debit: {float(item['debit']):>10} | Credit: {float(item['credit']):>10} | Solde: {float(item['solde']):>10}")
        total_debit += item['debit']
        total_credit += item['credit']
        
    print("-" * 80)
    print(f"{'Total':<43} | Debit: {float(total_debit):>10} | Credit: {float(total_credit):>10}")
    
    # 5. Commit so we can see it in UI
    db.session.commit()
    
    print("\nDonnées de test enregistrées en BD.")
