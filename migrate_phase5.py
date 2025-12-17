"""
Apply Phase 5 Migration and Initialize Default Accounts
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app, db
from app.comptabilite.service import ComptabiliteService
import psycopg2
from psycopg2 import sql

def apply_migration():
    """Apply the SQL migration."""
    app = create_app()
    
    with app.app_context():
        # Read the migration SQL
        migration_file = Path(__file__).parent / 'migrations' / 'phase5_comptabilite.sql'
        
        if not migration_file.exists():
            print(f"[ERROR] Migration file not found: {migration_file}")
            return False
        
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # Get database connection from SQLAlchemy
        connection = db.engine.raw_connection()
        
        try:
            cursor = connection.cursor()
            
            print("[INFO] Applying Phase 5 migration...")
            
            # Execute the migration
            cursor.execute(migration_sql)
            connection.commit()
            
            print("[SUCCESS] Migration applied successfully!")
            
            cursor.close()
            return True
            
        except Exception as e:
            connection.rollback()
            print(f"[ERROR] Error applying migration: {e}")
            return False
        finally:
            connection.close()

def initialize_accounts():
    """Initialize default chart of accounts."""
    app = create_app()
    
    with app.app_context():
        try:
            print("\n[INFO] Initializing default chart of accounts...")
            ComptabiliteService.initialize_default_accounts()
            print("[SUCCESS] Default accounts initialized successfully!")
            return True
        except Exception as e:
            print(f"[ERROR] Error initializing accounts: {e}")
            return False

def main():
    """Main migration function."""
    print("=" * 60)
    print("Phase 5: Comptabilite Notariale - Migration")
    print("=" * 60)
    
    # Step 1: Apply SQL migration
    if not apply_migration():
        print("\n[ERROR] Migration failed. Aborting.")
        return 1
    
    # Step 2: Initialize default accounts
    if not initialize_accounts():
        print("\n[WARNING] Migration succeeded but account initialization failed.")
        print("You can initialize accounts manually later.")
        return 1
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Phase 5 migration completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Restart the Flask application")
    print("2. Navigate to /comptabilite to access the accounting module")
    print("3. Run the test workflow to verify functionality")
    
    return 0

if __name__ == '__main__':
    exit(main())
