from sqlalchemy import create_engine, text
import sys

def migrate(url):
    engine = create_engine(url)
    with engine.begin() as conn:
        print("--- Fixing 'templates.contenu' Nullable Constraint ---")
        try:
            conn.execute(text("ALTER TABLE templates ALTER COLUMN contenu DROP NOT NULL"))
            print("Successfully removed NOT NULL constraint from 'templates.contenu'.")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fix_templates_nullable.py <DATABASE_URL>")
        sys.exit(1)
    migrate(sys.argv[1])
