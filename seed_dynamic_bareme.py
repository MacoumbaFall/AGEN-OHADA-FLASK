import sys
import os
from decimal import Decimal

# Add project root to path
sys.path.append(os.getcwd())

from app import create_app, db
from app.models import BaremeModele, BaremeVariable, BaremeLigneCalcul

app = create_app()

def seed_bareme_vente():
    with app.app_context():
        # 1. Clean up existing Vente barème
        existing = BaremeModele.query.filter_by(code='VENTE').first()
        if existing:
            db.session.delete(existing)
            db.session.commit()
            print("Suppression de l'ancien barème VENTE...")

        # 2. Créer le Modèle de Barème
        bareme = BaremeModele(
            code='VENTE',
            nom='Vente Immobilière',
            description="Calcul complet des honoraires, droits d'enregistrement et conservation foncière pour une vente."
        )
        db.session.add(bareme)
        db.session.flush()

        # 3. Ajouter les Variables (Codes majuscules pour éviter les ambiguïtés)
        vars = [
            BaremeVariable(bareme_id=bareme.id, code='PRIX_VENTE', label='Prix de Vente / Capital', type_champ='MONTANT', valeur_defaut='0', ordre=1),
            BaremeVariable(bareme_id=bareme.id, code='TAUX_ENREG', label="Taux d'Enregistrement (%)", type_champ='CHOIX', choix_json=[1, 2, 5, 10], valeur_defaut='10', ordre=2),
            BaremeVariable(bareme_id=bareme.id, code='MORCELLEMENT', label='Morcellement ou Titre Foncier existant ?', type_champ='BOOLEEN', valeur_defaut='True', ordre=3)
        ]
        db.session.add_all(vars)

        # 4. Ajouter les Lignes de Calcul (Règles dynamiques)
        lignes = [
            BaremeLigneCalcul(bareme_id=bareme.id, ordre=1, code='HONORAIRES_REDUIT', libelle='Honoraires Notariés (Taux Réduit)', 
                              type_ligne='TRANCHES', condition_affichage='TAUX_ENREG == 1', formule_ou_montant='PRIX_VENTE', 
                              tranches_json=[{"max": 20000000, "taux": 2.25}, {"max": 60000000, "taux": 1.5}, {"max": 220000000, "taux": 0.75}, {"max": None, "taux": 0.375}], soumis_tva=True),
            BaremeLigneCalcul(bareme_id=bareme.id, ordre=2, code='HONORAIRES_NORMAL', libelle='Honoraires Notariés', 
                              type_ligne='TRANCHES', condition_affichage='TAUX_ENREG != 1', formule_ou_montant='PRIX_VENTE', 
                              tranches_json=[{"max": 20000000, "taux": 4.5}, {"max": 60000000, "taux": 3.0}, {"max": 220000000, "taux": 1.5}, {"max": None, "taux": 0.75}], soumis_tva=True),
            BaremeLigneCalcul(bareme_id=bareme.id, ordre=3, code='ENREGISTREMENT', libelle="Droits d'Enregistrement", 
                              type_ligne='FORMULE', formule_ou_montant='PRIX_VENTE * (TAUX_ENREG / 100)', soumis_tva=False),
            BaremeLigneCalcul(bareme_id=bareme.id, ordre=4, code='CONSERVATION', libelle='Conservation Foncière (1% + fixe)', 
                              type_ligne='FORMULE', condition_affichage='MORCELLEMENT', formule_ou_montant='(PRIX_VENTE // 1000 * 1000) * 0.01 + 5000', soumis_tva=False),
            BaremeLigneCalcul(bareme_id=bareme.id, ordre=5, code='FRAIS_MORCELLEMENT', libelle='Frais de Morcellement / Titre', 
                              type_ligne='FORMULE', condition_affichage='MORCELLEMENT', formule_ou_montant='22500', soumis_tva=False),
            BaremeLigneCalcul(bareme_id=bareme.id, ordre=6, code='MUTATION', libelle="Droits sur Mutation", 
                              type_ligne='FORMULE', condition_affichage='not MORCELLEMENT', formule_ou_montant='(PRIX_VENTE * 0.01) + 5000', soumis_tva=False),
            BaremeLigneCalcul(bareme_id=bareme.id, ordre=7, code='EXPEDITIONS', libelle='Expéditions & Publicité Foncière', 
                              type_ligne='FORFAIT', formule_ou_montant='50000', soumis_tva=False),
            BaremeLigneCalcul(bareme_id=bareme.id, ordre=8, code='DIVERS', libelle='Frais Divers (Timbres, etc.)', 
                              type_ligne='FORFAIT', formule_ou_montant='50000', soumis_tva=False)
        ]
        db.session.add_all(lignes)
        db.session.commit()
        print("Barème VENTE injecté avec succès !")


if __name__ == "__main__":
    seed_bareme_vente()
