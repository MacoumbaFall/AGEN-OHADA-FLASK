---
description: Automated testing of Phase 5 (Comptabilité) - Backend Setup and Initialization
---

# Test Workflow - Phase 5: Comptabilité (Backend Testing)

// turbo-all

This workflow tests the Phase 5 accounting module backend setup, migration, and core functionality.

## Prerequisites
- Database must be running and accessible
- Flask application dependencies installed

## Test Steps

### 1. Apply Phase 5 Migration
```powershell
cd C:\Users\Admin\Documents\Repository\AGEN-OHADA-flask\AGEN-OHADA-FLASK
python migrate_phase5.py
```

**Expected Output:**
- Migration SQL applied successfully
- Default chart of accounts initialized
- Success message displayed

### 2. Verify Database Tables
```powershell
python -c "from app import create_app, db; from app.models import Recu, Facture, ComptaCompte; app = create_app(); app.app_context().push(); print('Recus table:', db.session.query(Recu).count()); print('Factures table:', db.session.query(Facture).count()); print('Comptes:', db.session.query(ComptaCompte).count())"
```

**Expected Output:**
- Recus table: 0
- Factures table: 0
- Comptes: 11 (default accounts)

### 3. Test Account Creation
```powershell
python -c "from app import create_app, db; from app.comptabilite.service import ComptabiliteService; app = create_app(); app.app_context().push(); compte = ComptabiliteService.create_compte('TEST-001', 'Test Account', 'GENERAL', 'OFFICE'); print(f'Created account: {compte.numero_compte} - {compte.libelle}')"
```

**Expected Output:**
- Created account: TEST-001 - Test Account

### 4. Test Receipt Creation
```powershell
python -c "from app import create_app, db; from app.comptabilite.service import ComptabiliteService; from datetime import date; app = create_app(); app.app_context().push(); recu = ComptabiliteService.create_recu(date.today(), 50000, 'ESPECES', 'Test receipt payment'); print(f'Created receipt: {recu.numero_recu} - {recu.montant} FCFA')"
```

**Expected Output:**
- Created receipt: REC-000001 - 50000.0 FCFA

### 5. Test Invoice Creation
```powershell
python -c "from app import create_app, db; from app.comptabilite.service import ComptabiliteService; from datetime import date; app = create_app(); app.app_context().push(); facture = ComptabiliteService.create_facture(date.today(), 100000, 'Test invoice for services'); print(f'Created invoice: {facture.numero_facture} - {facture.montant_ttc} FCFA')"
```

**Expected Output:**
- Created invoice: FACT-000001 - 100000.0 FCFA

### 6. Test Balance Calculation
```powershell
python -c "from app import create_app, db; from app.comptabilite.service import ComptabiliteService; from app.models import ComptaCompte; app = create_app(); app.app_context().push(); compte = db.session.query(ComptaCompte).filter_by(numero_compte='531-CLIENT').first(); if compte: print(f'Compte: {compte.libelle}'); print(f'Solde: {ComptabiliteService.get_balance(compte.id)} FCFA')"
```

**Expected Output:**
- Compte: Caisse - Compte Client
- Solde: 50000.0 FCFA (from the test receipt)

### 7. Test Trial Balance
```powershell
python -c "from app import create_app, db; from app.comptabilite.service import ComptabiliteService; app = create_app(); app.app_context().push(); balance = ComptabiliteService.get_balance_generale(); print(f'Accounts with balance: {len(balance)}'); total_debit = sum(item['debit'] for item in balance); total_credit = sum(item['credit'] for item in balance); print(f'Total Debit: {total_debit}'); print(f'Total Credit: {total_credit}'); print(f'Balanced: {abs(total_debit - total_credit) < 0.01}')"
```

**Expected Output:**
- Accounts with balance: 2 (or more)
- Total Debit: 50000.0
- Total Credit: 50000.0
- Balanced: True

### 8. Test General Ledger
```powershell
python -c "from app import create_app, db; from app.comptabilite.service import ComptabiliteService; app = create_app(); app.app_context().push(); ledger = ComptabiliteService.get_grand_livre(); print(f'Total movements: {len(ledger)}'); if ledger: print(f'First entry: {ledger[0][\"libelle\"]}')"
```

**Expected Output:**
- Total movements: 2 (debit and credit from receipt)
- First entry: Reçu REC-000001 - Test receipt payment

### 9. Verify Double-Entry Bookkeeping
```powershell
python -c "from app import create_app, db; from app.models import ComptaEcriture; app = create_app(); app.app_context().push(); ecriture = db.session.query(ComptaEcriture).first(); if ecriture: print(f'Entry: {ecriture.libelle_operation}'); print(f'Balanced: {ecriture.is_balanced()}'); print(f'Total: {ecriture.get_total()} FCFA'); print(f'Validated: {ecriture.valide}')"
```

**Expected Output:**
- Entry: Reçu REC-000001 - Test receipt payment
- Balanced: True
- Total: 50000.0 FCFA
- Validated: True

### 10. Start Flask Application
```powershell
python run.py
```

**Expected Output:**
- Flask app starts successfully
- Running on http://127.0.0.1:5000
- No errors in startup

## Success Criteria

✅ Migration applied successfully
✅ Default accounts created (11 accounts)
✅ Can create new accounts
✅ Can create receipts with auto-numbering (REC-000001)
✅ Can create invoices with auto-numbering (FACT-000001)
✅ Receipts create balanced accounting entries automatically
✅ Balance calculation works correctly
✅ Trial balance is balanced (debits = credits)
✅ General ledger shows all movements
✅ Double-entry bookkeeping is enforced
✅ Flask application starts without errors

## Expected Results

- **Database**: New tables created (recus, factures)
- **Accounts**: 11 default accounts initialized
- **Receipts**: Auto-numbered starting from REC-000001
- **Invoices**: Auto-numbered starting from FACT-000001
- **Accounting**: All entries are balanced
- **Reports**: Balance and ledger reports work correctly

## Notes

- All monetary amounts are in FCFA (West African CFA Franc)
- The system uses double-entry bookkeeping
- Office and Client accounts are strictly separated
- All entries must be balanced before validation
- Receipts automatically create and validate accounting entries
