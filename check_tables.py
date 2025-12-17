import psycopg

try:
    conn = psycopg.connect("dbname=agen_ohada user=postgres host=localhost port=5432")
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
    """)
    tables = cur.fetchall()
    print("Tables found in DB:")
    for t in tables:
        print(f"- {t[0]}")
    conn.close()
except Exception as e:
    print(e)
