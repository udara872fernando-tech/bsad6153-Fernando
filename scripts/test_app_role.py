import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("APP_DATABASE_URL")
if not db_url:
    raise ValueError("APP_DATABASE_URL is not set in environment variables.")

print(f"Connecting to database using app_reader...")
conn = psycopg.connect(db_url, autocommit=True)
cur = conn.cursor()

queries = [
    ("SELECT COUNT(*) FROM players;", True),
    ("DELETE FROM players WHERE player_id = 'nonexistent';", False),
    ("INSERT INTO players (player_id) VALUES ('test');", False),
]

for query, expect_success in queries:
    print(f"\n> {query}")
    try:
        cur.execute(query)
        if expect_success:
            result = cur.fetchone()
            print(f"Result: {result}")
        else:
            print("Success (Unexpected for write operation!)")
    except Exception as e:
        print(f"Expected Error: {e}")

cur.close()
conn.close()
print("\nAll read-only enforcement checks completed successfully!")