# Data Dictionary, Lineage, and Operations (As of 2026-11-22)

## 1. Data Dictionary & Known Caveats

| Table | Row Count (`2026-11-22`) | Primary Purpose | Load Behavior | Known Caveats / Quality Findings |
| :--- | :---: | :--- | :--- | :--- |
| `players` | 9,422 | Core player catalog (`player_id`, name, `position`, `team`, attributes) | Duplicate `player_id`s skipped (`ON CONFLICT DO NOTHING`) | `team` is `NULL` for 70.9% of players; 18 normalized `first_name + last_name + position` groups have duplicate `player_id`s |
| `rosters` | 10 | Fantasy roster records (`roster_id`, league/owner context, win/loss totals) | Duplicate keys skipped (`ON CONFLICT DO NOTHING`) | Represents fantasy rosters, not full NFL team rosters |
| `player_stats` | 9,423 | Player fantasy points and stat rows across weeks/seasons | Idempotent `UPSERT` (`ON CONFLICT DO UPDATE`) | Scoped to ingested weeks/seasons and available stat fields |

## 2. Data Lineage
1. **Upstream Source (Sleeper API):** Public read-only endpoints (`/state/nfl`, `/players/nfl/trending/add|drop`, `/players/nfl`, plus optional league endpoints when `SLEEPER_LEAGUE_ID` is configured).
2. **Extract / Fetch (`ingest/fetch.py`):** Paces requests (`0.5s` delay with `Retry-After` and exponential backoff), enforces the once-per-day refresh check on `players_all.json`, writes raw JSON payloads under `data/raw/`, and returns exit code `1` when `summary["failed"]` is non-empty.
3. **Load (`ingest/load.py`):** Connects via `DATABASE_URL`, skips duplicate `players` and `rosters` rows, `UPSERT`s `player_stats`, and exits non-zero on failure.
4. **Quality & Evaluation (`db/quality_checks.sql`, `docs/data_quality.md`, `evals/golden_questions.csv`, `evals/check_reference.py`):** Tracks data quality issues and verifies reference SQL queries via `APP_DATABASE_URL` (`app_reader`).

## 3. Freshness Guarantee & Schedule
- **Workflow Cadence:** Scheduled every 6 hours (`0 */6 * * *`) in GitHub Actions, with manual `workflow_dispatch` runs supported.
- **Player Catalog Cache:** `players_all.json` refreshes at most once every 24 hours unless forced or expired.

## 4. Change Log & Ownership
- **Branch & Scope:** `milestone-3` covering Parts D–H (scheduled sync & non-zero load failure handling, SQL quality checks & report, golden questions & reference SQL checker, failure drills log, and data dictionary/lineage).
- **Owner:** Udara Fernando (`bsad6153-Fernando`) — BSAD 6153.
