---
description: Automated testing of Phase 5 (Comptabilité) - UI Flow (Accounts, Receipts, Invoices, Reports)
---

# Test Workflow - Phase 5: Comptabilité (UI Testing)

This workflow tests the Phase 5 accounting module UI using the browser integration.

## Prerequisites
- Flask application must be running (`python run.py`)
- Admin user must exist (default: `admin` / `admin123`)
- Database must be initialized with default accounts

## Test Steps

### 1. Start Application (if not running)
```powershell
# In a separate terminal
python run.py
```

### 2. Browser Test Flow
The following steps will be executed by the browser agent:

1.  **Login**
    - Navigate to `http://127.0.0.1:5000/auth/login`
    - Login with `admin` / `admin123`

2.  **Dashboard**
    - Verify redirection to Dashboard or navigate to `http://127.0.0.1:5000/comptabilite/`
    - Check for stats widgets (Total Facturé, Recettes, etc.)

3.  **Accounts Management**
    - Navigate to "Plan Comptable" (`/comptabilite/comptes`)
    - Click "Initialiser" if the list is empty
    - Create a new account:
        - Number: `411100`
        - Label: `Client TEST UI`
        - Type: `Client`
        - Category: `Compte Client`
    - Verify the account appears in the list

4.  **Receipts Management**
    - Navigate to "Reçus" (`/comptabilite/recus`)
    - Click "Nouveau Reçu"
    - Fill form:
        - Date: Today
        - Amount: `150000`
        - Payment Mode: `Virement`
        - Reference: `VIR-TEST-UI-001`
        - Motif: `Provision sur frais`
    - Submit
    - Verify redirection to Receipt View
    - Verify details match input

5.  **Invoices Management**
    - Navigate to "Factures" (`/comptabilite/factures`)
    - Click "Nouvelle Facture"
    - Fill form:
        - Date: Today
        - Amount HT: `250000`
        - Description: `Honoraires Dossier X`
    - Submit
    - Verify redirection to Invoice View
    - Verify calculations (TVA if applicable, Total)

6.  **Reports**
    - Navigate to "Balance Générale" (`/comptabilite/reports/balance`)
    - Verify the receipt amount appears in the correct accounts (Bank/Client funds) and creates a balanced entry.
    - Navigate to "Grand Livre" (`/comptabilite/reports/grand-livre`)
    - Select the client account created earlier
    - Verify the transaction appears

## Success Criteria

✅ Login successful
✅ Dashboard loads with stats
✅ Can create a new account via UI
✅ Can emit a new receipt (Recu) via UI
✅ Can create a new invoice (Facture) via UI
✅ Receipt automatically generates accounting entries (visible in Balance/Ledger)
