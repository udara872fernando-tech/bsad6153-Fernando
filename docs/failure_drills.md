# Failure Drills (2026-11-22)

## 1. Bad Database Credentials (`DATABASE_URL`)
- **What broke:** Temporarily pointed `DATABASE_URL` to an invalid PostgreSQL connection target and ran `ingest/load.py`.
- **Observed behavior:** Failed immediately with `psycopg2.OperationalError` and exit code `1`; existing database tables remained untouched.
- **Recovery:** Restored the valid `DATABASE_URL` in the environment and verified normal load behavior.

## 2. Bad API URL / Upstream Fetch Failure
- **What broke:** Tested invalid/unreachable API endpoint behavior in the fetch step (`ingest/fetch.py`).
- **Observed behavior:** Failed endpoints are tracked in `summary["failed"]` and cause `ingest/fetch.py` to exit with code `1` without writing error payloads as valid data.
- **Recovery:** Restored `BASE_URL` in `ingest/fetch.py` and verified a clean fetch run (`exit code: 0`).

## 3. Repeated Sync Run (Idempotency)
- **What broke:** Executed `ingest/load.py` twice back-to-back on the same input data.
- **Observed behavior:** Both runs exited with code `0`; `players` (9,422 rows) and `rosters` skipped duplicates, while `player_stats` ran `UPSERT` with no duplicate rows created.
- **Recovery:** No rollback required; idempotent load logic preserved table integrity.
