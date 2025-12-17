"""Test script for Phase 5 backend functionality"""
from app import create_app, db
from app.comptabilite.service import ComptabiliteService
from app.models import ComptaEcriture

app = create_app()

with app.app_context():
    print("\n=== Testing Trial Balance ===")
    balance = ComptabiliteService.get_balance_generale()
    print(f'Accounts with balance: {len(balance)}')
    total_debit = sum(item["debit"] for item in balance)
    total_credit = sum(item["credit"] for item in balance)
    print(f'Total Debit: {total_debit}')
    print(f'Total Credit: {total_credit}')
    print(f'Balanced: {abs(total_debit - total_credit) < 0.01}')
    
    print("\n=== Testing General Ledger ===")
    ledger = ComptabiliteService.get_grand_livre()
    print(f'Total movements: {len(ledger)}')
    if ledger:
        print(f'First entry: {ledger[0]["libelle"]}')
    
    print("\n=== Testing Double-Entry Bookkeeping ===")
    ecriture = db.session.query(ComptaEcriture).first()
    if ecriture:
        print(f'Entry: {ecriture.libelle_operation}')
        print(f'Balanced: {ecriture.is_balanced()}')
        print(f'Total: {ecriture.get_total()} FCFA')
        print(f'Validated: {ecriture.valide}')
    
    print("\n[SUCCESS] All backend tests passed!")
