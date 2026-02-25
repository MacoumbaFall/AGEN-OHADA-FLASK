"""
Service layer for accounting operations.
Handles business logic for double-entry bookkeeping, account management, and financial operations.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Optional, Tuple
from sqlalchemy import and_, or_, func
from app import db
from app.models import ComptaCompte, ComptaEcriture, ComptaMouvement, Recu, Facture, Dossier, Client, User

class ComptabiliteService:
    """Service class for accounting operations."""
    
    # Standard account numbers (can be customized)
    COMPTE_BANQUE_OFFICE = '512-OFFICE'
    COMPTE_CAISSE_OFFICE = '531-OFFICE'
    COMPTE_BANQUE_CLIENT = '512-CLIENT'
    COMPTE_CAISSE_CLIENT = '531-CLIENT'
    COMPTE_HONORAIRES = '706'
    COMPTE_CLIENTS_DEBITEURS = '411'
    
    @staticmethod
    def create_compte(numero: str, libelle: str, type_compte: str, categorie: str = None) -> ComptaCompte:
        """Create a new account."""
        compte = ComptaCompte(
            numero_compte=numero,
            libelle=libelle,
            type_compte=type_compte,
            categorie=categorie,
            actif=True
        )
        db.session.add(compte)
        db.session.commit()
        return compte
    
    @staticmethod
    def initialize_default_accounts():
        """Initialize the default chart of accounts."""
        default_accounts = [
            # Office Accounts - Actif / Passif (Bilan)
            ('512-OFFICE', 'Banque - Compte Office', 'GENERAL', 'OFFICE'),
            ('531-OFFICE', 'Caisse - Compte Office', 'GENERAL', 'OFFICE'),
            ('401', 'Fournisseurs d\'exploitation', 'GENERAL', 'OFFICE'),
            ('411', 'Clients - Honoraires dus', 'GENERAL', 'OFFICE'),
            ('419', 'Clients - Avances et acomptes reçus', 'GENERAL', 'OFFICE'),
            ('421', 'Personnel - Rémunérations dues', 'GENERAL', 'OFFICE'),
            ('431', 'Sécurité sociale', 'GENERAL', 'OFFICE'),
            ('442', 'État - Droits d\'enregistrement et Conservation', 'GENERAL', 'OFFICE'),
            ('443', 'État - TVA facturée', 'GENERAL', 'OFFICE'),
            ('445', 'État - TVA récupérable', 'GENERAL', 'OFFICE'),
            ('462', 'Débours payés pour le compte des clients', 'GENERAL', 'OFFICE'),
            ('471', 'Comptes d\'Attente', 'GENERAL', 'OFFICE'),
            
            # Office Accounts - Charges (Classe 6)
            ('605', 'Fournitures de bureau', 'CHARGE', 'OFFICE'),
            ('613', 'Locations', 'CHARGE', 'OFFICE'),
            ('622', 'Rémunérations d\'intermédiaires et honoraires', 'CHARGE', 'OFFICE'),
            ('631', 'Frais bancaires', 'CHARGE', 'OFFICE'),
            ('641', 'Impôts et taxes', 'CHARGE', 'OFFICE'),
            ('661', 'Charges de personnel', 'CHARGE', 'OFFICE'),
            
            # Office Accounts - Produits (Classe 7)
            ('706', 'Honoraires - Prestations de services', 'PRODUIT', 'OFFICE'),
            ('708', 'Produits des activités annexes', 'PRODUIT', 'OFFICE'),
            
            # Client Accounts (Trust Funds)
            ('512-CLIENT', 'Banque - Compte Client', 'GENERAL', 'CLIENT'),
            ('531-CLIENT', 'Caisse - Compte Client', 'GENERAL', 'CLIENT'),
            ('467', 'Fonds de Tiers - Clients', 'CLIENT', 'CLIENT'),
        ]
        
        for numero, libelle, type_compte, categorie in default_accounts:
            existing = db.session.execute(
                db.select(ComptaCompte).filter_by(numero_compte=numero)
            ).scalar_one_or_none()
            
            if not existing:
                ComptabiliteService.create_compte(numero, libelle, type_compte, categorie)
    
    @staticmethod
    def create_ecriture(date_ecriture: date, libelle: str, journal_code: str,
                       mouvements: List[Dict], dossier_id: int = None,
                       numero_piece: str = None, user_id: int = None) -> ComptaEcriture:
        """
        Create a new accounting entry with movements.
        
        Args:
            date_ecriture: Date of the entry
            libelle: Description of the operation
            journal_code: Journal code (BQ, CA, OD, VT)
            mouvements: List of movements [{'compte_id': int, 'debit': float, 'credit': float}]
            dossier_id: Optional dossier ID
            numero_piece: Optional piece number (receipt, invoice, etc.)
            user_id: User creating the entry
            
        Returns:
            ComptaEcriture: The created entry
            
        Raises:
            ValueError: If the entry is not balanced
        """
        # Create the entry
        ecriture = ComptaEcriture(
            date_ecriture=date_ecriture,
            libelle_operation=libelle,
            journal_code=journal_code,
            dossier_id=dossier_id,
            numero_piece=numero_piece,
            created_by=user_id,
            valide=False
        )
        db.session.add(ecriture)
        db.session.flush()  # Get the ID
        
        # Create movements
        total_debit = Decimal('0')
        total_credit = Decimal('0')
        
        for mouv_data in mouvements:
            mouvement = ComptaMouvement(
                ecriture_id=ecriture.id,
                compte_id=mouv_data['compte_id'],
                debit=Decimal(str(mouv_data.get('debit', 0))),
                credit=Decimal(str(mouv_data.get('credit', 0)))
            )
            db.session.add(mouvement)
            total_debit += mouvement.debit
            total_credit += mouvement.credit
        
        # Check if balanced
        if abs(total_debit - total_credit) > Decimal('0.01'):
            raise ValueError(f"Entry not balanced: Debit={total_debit}, Credit={total_credit}")
        
        db.session.commit()
        return ecriture
    
    @staticmethod
    def valider_ecriture(ecriture_id: int) -> ComptaEcriture:
        """Validate an accounting entry (make it permanent)."""
        ecriture = db.session.get(ComptaEcriture, ecriture_id)
        if not ecriture:
            raise ValueError("Entry not found")
        
        if not ecriture.is_balanced():
            raise ValueError("Cannot validate unbalanced entry")
        
        ecriture.valide = True
        db.session.commit()
        return ecriture
    
    @staticmethod
    def create_recu(date_emission: date, montant: float, mode_paiement: str,
                   motif: str, dossier_id: int = None, client_id: int = None,
                   reference_paiement: str = None, user_id: int = None) -> Recu:
        """
        Create a receipt and the corresponding accounting entry.
        
        Args:
            date_emission: Date of receipt
            montant: Amount
            mode_paiement: Payment method (ESPECES, CHEQUE, VIREMENT)
            motif: Purpose/description
            dossier_id: Optional dossier ID
            client_id: Optional client ID
            reference_paiement: Optional payment reference
            user_id: User creating the receipt
            
        Returns:
            Recu: The created receipt
        """
        # Generate receipt number
        last_recu = db.session.execute(
            db.select(Recu).order_by(Recu.id.desc())
        ).scalars().first()
        
        if last_recu:
            last_num = int(last_recu.numero_recu.split('-')[1])
            numero_recu = f"REC-{last_num + 1:06d}"
        else:
            numero_recu = "REC-000001"
        
        # Determine accounts based on payment method
        if mode_paiement == 'ESPECES':
            compte_tresorerie_id = db.session.execute(
                db.select(ComptaCompte.id).filter_by(numero_compte=ComptabiliteService.COMPTE_CAISSE_CLIENT)
            ).scalar_one()
        else:  # CHEQUE or VIREMENT
            compte_tresorerie_id = db.session.execute(
                db.select(ComptaCompte.id).filter_by(numero_compte=ComptabiliteService.COMPTE_BANQUE_CLIENT)
            ).scalar_one()
        
        compte_client_id = db.session.execute(
            db.select(ComptaCompte.id).filter_by(numero_compte='467')
        ).scalar_one()
        
        # Create accounting entry
        mouvements = [
            {'compte_id': compte_tresorerie_id, 'debit': montant, 'credit': 0},
            {'compte_id': compte_client_id, 'debit': 0, 'credit': montant}
        ]
        
        ecriture = ComptabiliteService.create_ecriture(
            date_ecriture=date_emission,
            libelle=f"Reçu {numero_recu} - {motif}",
            journal_code='CA' if mode_paiement == 'ESPECES' else 'BQ',
            mouvements=mouvements,
            dossier_id=dossier_id,
            numero_piece=numero_recu,
            user_id=user_id
        )
        
        # Validate the entry immediately
        ComptabiliteService.valider_ecriture(ecriture.id)
        
        # Create the receipt
        recu = Recu(
            numero_recu=numero_recu,
            date_emission=date_emission,
            dossier_id=dossier_id,
            client_id=client_id,
            montant=montant,
            mode_paiement=mode_paiement,
            reference_paiement=reference_paiement,
            motif=motif,
            ecriture_id=ecriture.id,
            created_by=user_id
        )
        db.session.add(recu)
        db.session.commit()
        
        return recu
    
    @staticmethod
    def create_facture(date_emission: date, montant_ht: float, description: str,
                      dossier_id: int = None, client_id: int = None,
                      montant_tva: float = 0, date_echeance: date = None,
                      user_id: int = None) -> Facture:
        """Create an invoice and its corresponding accounting entry."""
        # Generate invoice number
        last_facture = db.session.execute(
            db.select(Facture).order_by(Facture.id.desc())
        ).scalars().first()
        
        if last_facture:
            last_num = int(last_facture.numero_facture.split('-')[1])
            numero_facture = f"FACT-{last_num + 1:06d}"
        else:
            numero_facture = "FACT-000001"
        
        montant_ttc = montant_ht + montant_tva
        
        # 1. Create the accounting entry for the invoice (VT - Ventes)
        compte_client = db.session.execute(db.select(ComptaCompte).filter_by(numero_compte='411')).scalar_one_or_none()
        compte_honoraires = db.session.execute(db.select(ComptaCompte).filter_by(numero_compte='706')).scalar_one_or_none()
        compte_tva = db.session.execute(db.select(ComptaCompte).filter_by(numero_compte='443')).scalar_one_or_none()
        # Fallback if specific accounts are missing
        if not compte_tva:
             compte_tva = db.session.execute(db.select(ComptaCompte).filter_by(numero_compte='445')).scalar_one_or_none()
             
        ecriture_id = None
        if compte_client and compte_honoraires:
            mouvements = [
                {'compte_id': compte_client.id, 'debit': float(montant_ttc), 'credit': 0},
                {'compte_id': compte_honoraires.id, 'debit': 0, 'credit': float(montant_ht)}
            ]
            if compte_tva and montant_tva > 0:
                mouvements.append({'compte_id': compte_tva.id, 'debit': 0, 'credit': float(montant_tva)})
                
            ecriture = ComptabiliteService.create_ecriture(
                date_ecriture=date_emission,
                libelle=f"Facture {numero_facture} - {description}",
                journal_code='VT',
                mouvements=mouvements,
                dossier_id=dossier_id,
                numero_piece=numero_facture,
                user_id=user_id
            )
            ComptabiliteService.valider_ecriture(ecriture.id)
            ecriture_id = ecriture.id
        
        # 2. Create the invoice
        facture = Facture(
            numero_facture=numero_facture,
            date_emission=date_emission,
            date_echeance=date_echeance,
            dossier_id=dossier_id,
            client_id=client_id,
            montant_ht=montant_ht,
            montant_tva=montant_tva,
            montant_ttc=montant_ttc,
            statut='IMPAYEE',
            description=description,
            ecriture_id=ecriture_id,
            created_by=user_id
        )
        db.session.add(facture)
        db.session.commit()
        
        return facture
    
    @staticmethod
    def get_balance(compte_id: int, date_debut: date = None, date_fin: date = None) -> Decimal:
        """Get the balance of an account for a given period."""
        query = db.select(ComptaMouvement).join(ComptaEcriture).filter(
            ComptaMouvement.compte_id == compte_id,
            ComptaEcriture.valide == True
        )
        
        if date_debut:
            query = query.filter(ComptaEcriture.date_ecriture >= date_debut)
        if date_fin:
            query = query.filter(ComptaEcriture.date_ecriture <= date_fin)
        
        mouvements = db.session.execute(query).scalars().all()
        
        total_debit = sum(Decimal(str(m.debit)) for m in mouvements)
        total_credit = sum(Decimal(str(m.credit)) for m in mouvements)
        
        return total_debit - total_credit
    
    @staticmethod
    def get_grand_livre(compte_id: int = None, date_debut: date = None, date_fin: date = None) -> List[Dict]:
        """
        Get the general ledger (Grand Livre).
        
        Returns a list of structured dictionaries for the template to group by account.
        """
        query_comptes = db.select(ComptaCompte).filter_by(actif=True)
        if compte_id:
            query_comptes = query_comptes.filter_by(id=compte_id)
        
        comptes = db.session.execute(query_comptes.order_by(ComptaCompte.numero_compte)).scalars().all()
        
        result = []
        for compte in comptes:
            # 1. Calculer le solde initial (tous les mouvements AVANT date_debut)
            solde_initial = Decimal('0')
            if date_debut:
                mouvements_initiaux = db.session.execute(
                    db.select(ComptaMouvement).join(ComptaEcriture).filter(
                        ComptaMouvement.compte_id == compte.id,
                        ComptaEcriture.valide == True,
                        ComptaEcriture.date_ecriture < date_debut
                    )
                ).scalars().all()
                for mouv in mouvements_initiaux:
                    solde_initial += Decimal(str(mouv.debit)) - Decimal(str(mouv.credit))
            
            # 2. Récupérer les mouvements de la période
            query_mouv = db.select(ComptaMouvement).join(ComptaEcriture).filter(
                ComptaMouvement.compte_id == compte.id,
                ComptaEcriture.valide == True
            )
            
            if date_debut:
                query_mouv = query_mouv.filter(ComptaEcriture.date_ecriture >= date_debut)
            if date_fin:
                query_mouv = query_mouv.filter(ComptaEcriture.date_ecriture <= date_fin)
                
            query_mouv = query_mouv.order_by(ComptaEcriture.date_ecriture, ComptaEcriture.id)
            mouvements = db.session.execute(query_mouv).scalars().all()
            
            # Si pas de mouvements et solde initial à 0, on peut ignorer le compte
            if not mouvements and solde_initial == Decimal('0'):
                continue
                
            compte_data = {
                'compte': compte,
                'solde_initial': solde_initial,
                'ecritures': [],
                'total_debit': Decimal('0'),
                'total_credit': Decimal('0'),
                'solde_final': solde_initial
            }
            
            solde_cumule = solde_initial
            
            for mouv in mouvements:
                montant = Decimal(str(mouv.debit)) - Decimal(str(mouv.credit))
                solde_cumule += montant
                
                compte_data['total_debit'] += Decimal(str(mouv.debit))
                compte_data['total_credit'] += Decimal(str(mouv.credit))
                
                compte_data['ecritures'].append({
                    'date_ecriture': mouv.ecriture.date_ecriture,
                    'libelle': mouv.ecriture.libelle_operation,
                    'piece_reference': mouv.ecriture.numero_piece or '',
                    'montant': montant,
                    'solde_cumule': solde_cumule
                })
            
            compte_data['solde_final'] = solde_cumule
            result.append(compte_data)
            
        return result
    
    @staticmethod
    def get_balance_generale(date_fin: date = None) -> List[Dict]:
        """
        Get the trial balance (Balance Générale).
        
        Returns a list of all accounts with their balances.
        """
        comptes = db.session.execute(
            db.select(ComptaCompte).filter_by(actif=True).order_by(ComptaCompte.numero_compte)
        ).scalars().all()
        
        result = []
        for compte in comptes:
            solde = ComptabiliteService.get_balance(compte.id, date_fin=date_fin)
            if solde != 0:  # Only show accounts with non-zero balance
                result.append({
                    'numero_compte': compte.numero_compte,
                    'libelle': compte.libelle,
                    'categorie': compte.categorie,
                    'debit': solde if solde > 0 else 0,
                    'credit': abs(solde) if solde < 0 else 0,
                    'solde': solde
                })
        
        return result


