import csv
import os
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()

CSV_PATH = os.path.join("evals", "golden_questions.csv")


def main():
    app_db_url = os.getenv("APP_DATABASE_URL")
    if not app_db_url:
        print("ERROR: APP_DATABASE_URL is not set in environment or .env", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(CSV_PATH):
        print(f"ERROR: {CSV_PATH} not found.", file=sys.stderr)
        sys.exit(1)

    failures = 0
    checked = 0

    conn = psycopg2.connect(app_db_url)
    try:
        with conn.cursor() as cur, open(CSV_PATH, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                qid = (row.get("id") or "").strip()
                category = (row.get("category") or "").strip()
                ref_sql = (row.get("reference_sql") or "").strip()

                if category == "should_decline" or not ref_sql:
                    print(f"[SKIP] {qid} ({category}): no reference_sql required")
                    continue

                checked += 1
                try:
                    cur.execute(ref_sql)
                    rows = cur.fetchall()
                    if not rows:
                        print(f"[FAIL] {qid}: returned 0 rows", file=sys.stderr)
                        failures += 1
                    else:
                        print(f"[PASS] {qid}: returned {len(rows)} row(s)")
                except Exception as exc:
                    conn.rollback()
                    print(f"[FAIL] {qid}: SQL error -> {exc}", file=sys.stderr)
                    failures += 1
    finally:
        conn.close()

    print(f"\nChecked {checked} SQL reference question(s); failures: {failures}")
    if failures > 0 or checked == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
