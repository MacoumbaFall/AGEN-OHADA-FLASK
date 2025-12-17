import os
import shutil
import datetime
import subprocess
from app.config import Config

def backup():
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f"backups/{timestamp}"
    os.makedirs(backup_dir, exist_ok=True)
    
    print(f"Starting backup to {backup_dir}...")
    
    # 1. Database Backup
    db_uri = Config.SQLALCHEMY_DATABASE_URI
    if 'sqlite' in db_uri:
        # Copy sqlite file
        db_path = db_uri.replace('sqlite:///', '')
        if os.path.exists(db_path):
            shutil.copy2(db_path, f"{backup_dir}/app.db")
            print("- SQLite database backed up.")
        else:
            print("- SQLite file not found!")
    else:
        # Assume Postgres
        try:
            # Requires pg_dump in path
            # db_uri format: postgresql://user:pass@host:port/dbname
            # This is a simplified extraction
            dbname = db_uri.split('/')[-1]
            subprocess.run(f"pg_dump {db_uri} > {backup_dir}/dump.sql", shell=True, check=True)
            print("- PostgreSQL database backed up.")
        except Exception as e:
            print(f"- Error backing up Postgres: {e}")

    # 2. Uploads Backup
    uploads_dir = 'app/static/docs' # Assuming this is where generated acts/etc go
    if os.path.exists(uploads_dir):
        shutil.make_archive(f"{backup_dir}/docs", 'zip', uploads_dir)
        print("- Documents directory zipped.")
    else:
        print("- No documents directory found.")
        
    print("Backup completed successfully.")

if __name__ == '__main__':
    backup()
