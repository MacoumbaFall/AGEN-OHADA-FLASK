from sqlalchemy import create_engine, text
import sys

def verify(url):
    engine = create_engine(url)
    tables = ['actes', 'templates']
    
    with engine.connect() as conn:
        for table in tables:
            print(f"\n--- Columns in table '{table}' ---")
            result = conn.execute(text(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{table}'
                ORDER BY ordinal_position;
            """))
            columns = result.all()
            if not columns:
                print(f"Table '{table}' not found or has no columns!")
            for col in columns:
                print(f"- {col[0]} ({col[1]})")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python db_verify.py <DATABASE_URL>")
        sys.exit(1)
    verify(sys.argv[1])
