from app import create_app, db
from app.models import Dossier, ComptaCompte, ComptaEcriture, ComptaMouvement, Recu, Facture
from sqlalchemy import func
import sys

def run_audit():
    app = create_app()
    with app.app_context():
        print("=== STARTING DATA INTEGRITY AUDIT ===")
        errors = []
        warnings = []

        # 1. Dossier Checks
        dossiers = db.session.execute(db.select(Dossier)).scalars().all()
        nums = [d.numero_dossier for d in dossiers]
        if len(nums) != len(set(nums)):
            errors.append(f"CRITICAL: Non-unique dossier numbers found! {len(nums) - len(set(nums))} duplicates.")
        else:
            print(f"OK: All {len(dossiers)} dossiers have unique numbers.")

        # 2. Accounting Internal Consistency
        # Sum of all movements should be 0 (Debit - Credit = 0)
        total_debit = db.session.query(func.sum(ComptaMouvement.debit)).scalar() or 0
        total_credit = db.session.query(func.sum(ComptaMouvement.credit)).scalar() or 0
        
        if total_debit != total_credit:
            errors.append(f"CRITICAL: Accounting Imbalance! Total Debit ({total_debit}) != Total Credit ({total_credit}). Diff: {total_debit - total_credit}")
        else:
            print(f"OK: General Ledger is balanced. Total: {total_debit} FCFA.")

        # 3. Double-Entry Validation (Each Ecriture must be balanced)
        ecritures = db.session.execute(db.select(ComptaEcriture)).scalars().all()
        for ec in ecritures:
            d = sum(m.debit for m in ec.mouvements)
            c = sum(m.credit for m in ec.mouvements)
            if d != c:
                errors.append(f"ERROR: Ecriture #{ec.id} ({ec.numero_ecriture}) is imbalanced! D:{d} C:{c}")
        
        if not any("Ecriture" in e for e in errors):
            print(f"OK: All {len(ecritures)} individual entries are balanced.")

        # 4. Orphans
        mouvements_without_account = db.session.query(ComptaMouvement).filter(ComptaMouvement.compte_id == None).count()
        if mouvements_without_account > 0:
            errors.append(f"CRITICAL: Found {mouvements_without_account} movements without an associated account.")
        else:
            print("OK: No orphaned movements found.")

        # 5. Receipts/Invoices Link
        recus = db.session.execute(db.select(Recu)).scalars().all()
        for r in recus:
            if not r.ecriture:
                warnings.append(f"WARN: Receipt {r.numero_recu} has no associated accounting entry.")
        
        print(f"OK: {len(recus)} receipts verified.")

        # Summary
        print("\n=== AUDIT SUMMARY ===")
        if not errors and not warnings:
            print("PASSED: All integrity checks passed.")
        else:
            for e in errors: print(f"[ERR] {e}")
            for w in warnings: print(f"[WARN] {w}")
            
        if errors:
            sys.exit(1)
        sys.exit(0)

if __name__ == "__main__":
    run_audit()
