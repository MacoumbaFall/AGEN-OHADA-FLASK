import os
import sys

print(f"FileSystem Encoding: {sys.getfilesystemencoding()}")

try:
    import psycopg
    print(f"Psycopg (v3) version: {psycopg.__version__}")
    print("\nAttempting minimal psycopg (v3) connection...")
    # psycopg 3 syntax
    conn = psycopg.connect(
        "dbname=agen_ohada user=postgres host=localhost port=5432"
    )
    print("Connection successful with psycopg 3!")
    conn.close()
except Exception as e:
    print(f"Psycopg 3 connection failed: {e}")
    import traceback
    traceback.print_exc()
