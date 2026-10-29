"""
ingest/fetch.py  -  Week 1: pull raw data from the Sleeper API and save it as JSON.

What it fetches (all public, read-only Sleeper endpoints, base https://api.sleeper.app/v1):
  1. /state/nfl                          -> current season + week
  2. /players/nfl/trending/add|drop      -> who is being picked up / dropped
  3. /players/nfl                        -> full player dictionary (~5 MB; at most once per day)
  4. /league/<id>/rosters, /users, /matchups/<week>   (only if SLEEPER_LEAGUE_ID is set in .env)

Where files go:
  data/raw/     full raw responses (Git-ignored: large data stays out of the repo)
  data/sample/  a few records from each response (small; safe to commit so others see the shape)

Run:  python ingest/fetch.py
"""

import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

try:
    from dotenv import load_dotenv
    load_dotenv()  # reads .env so optional settings like SLEEPER_LEAGUE_ID are available
except ImportError:
    pass  # .env support is optional; the script still works without it

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------
BASE_URL = "https://api.sleeper.app/v1"
ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
SAMPLE_DIR = ROOT / "data" / "sample"

# AUTHENTICATION / API KEY:
# Sleeper needs NO API key. The docs say: "No API Token is necessary, as you cannot
# modify contents via this API." So nothing is read from .env for auth and no
# Authorization header is sent. The only value read from .env is the OPTIONAL league
# ID below, which is not a secret (it is visible in any Sleeper league URL).
LEAGUE_ID = os.getenv("SLEEPER_LEAGUE_ID", "").strip()

# RATE LIMIT SETTINGS:
# Sleeper's rule: stay under 1000 calls per minute or risk an IP block.
# We pause 0.5 s between calls (max ~120/min), far below that limit.
SECONDS_BETWEEN_REQUESTS = 0.5
MAX_RETRIES = 4            # attempts per URL before giving up
TIMEOUT_SECONDS = 30
PLAYERS_MAX_AGE_HOURS = 24  # docs: call /players/nfl "once per day at most"
SAMPLE_SIZE = 5             # records kept per sample file

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("fetch")

# A run summary so the script can report what happened at the end.
summary = {"ok": [], "failed": [], "skipped": []}

session = requests.Session()
session.headers.update({"User-Agent": "bsad6153-fantasy-project (student)"})
_last_request_at = 0.0


# ---------------------------------------------------------------------------
# HTTP helper: polite pacing, retries, 429 handling
# ---------------------------------------------------------------------------
def get_json(path, params=None):
    """GET BASE_URL+path and return parsed JSON, or None if it ultimately fails.
    Never raises, so one bad endpoint cannot crash the whole run."""
    global _last_request_at, SECONDS_BETWEEN_REQUESTS
    url = f"{BASE_URL}{path}"

    for attempt in range(1, MAX_RETRIES + 1):
        # RATE LIMIT - WAIT BETWEEN REQUESTS:
        # Sleep so consecutive calls are at least SECONDS_BETWEEN_REQUESTS apart.
        wait = SECONDS_BETWEEN_REQUESTS - (time.monotonic() - _last_request_at)
        if wait > 0:
            time.sleep(wait)
        _last_request_at = time.monotonic()

        try:
            resp = session.get(url, params=params, timeout=TIMEOUT_SECONDS)
        except requests.RequestException as exc:
            # Network trouble (timeout, DNS, dropped connection): back off and retry.
            backoff = 2 ** attempt
            log.warning("%s -> network error (%s); retry %d/%d in %ds",
                        path, exc.__class__.__name__, attempt, MAX_RETRIES, backoff)
            time.sleep(backoff)
            continue

        # 429 TOO MANY REQUESTS:
        # We are going too fast. Honor the Retry-After header if Sleeper sends one,
        # otherwise use exponential backoff (2, 4, 8, 16 s), and slow ALL later
        # requests down by doubling the pause, then retry the same URL.
        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After")
            backoff = int(retry_after) if retry_after and retry_after.isdigit() else 2 ** attempt
            SECONDS_BETWEEN_REQUESTS = min(SECONDS_BETWEEN_REQUESTS * 2, 10)
            log.warning("%s -> 429 Too Many Requests; sleeping %ds (attempt %d/%d), "
                        "pause between calls now %.1fs",
                        path, backoff, attempt, MAX_RETRIES, SECONDS_BETWEEN_REQUESTS)
            time.sleep(backoff)
            continue

        # Temporary server problems: retry with backoff.
        if resp.status_code >= 500:
            backoff = 2 ** attempt
            log.warning("%s -> HTTP %d; retry %d/%d in %ds",
                        path, resp.status_code, attempt, MAX_RETRIES, backoff)
            time.sleep(backoff)
            continue

        # Other client errors (400 bad request, 404 not found) won't fix themselves.
        if resp.status_code != 200:
            log.error("%s -> HTTP %d (not retrying): %s",
                      path, resp.status_code, resp.text[:200])
            return None

        try:
            data = resp.json()
        except ValueError:
            log.error("%s -> response was not valid JSON", path)
            return None

        # Sleeper returns 200 with a JSON null for unknown IDs instead of a 404.
        if data is None:
            log.error("%s -> API returned null (unknown ID or no data)", path)
            return None
        return data

    log.error("%s -> gave up after %d attempts", path, MAX_RETRIES)
    return None


# ---------------------------------------------------------------------------
# Saving
# ---------------------------------------------------------------------------
def save(name, data):
    """Write the full raw response to data/raw/ and a few records to data/sample/."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

    raw_path = RAW_DIR / f"{name}.json"
    raw_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # Sample: first few items of a list, first few keys of a dict.
    if isinstance(data, list):
        sample = data[:SAMPLE_SIZE]
    elif isinstance(data, dict) and len(data) > SAMPLE_SIZE and name.startswith("players_all"):
        sample = dict(list(data.items())[:SAMPLE_SIZE])
    else:
        sample = data
    (SAMPLE_DIR / f"{name}.sample.json").write_text(json.dumps(sample, indent=2), encoding="utf-8")

    count = len(data) if isinstance(data, (list, dict)) else 1
    log.info("saved %-28s %6d records -> %s", name, count, raw_path.relative_to(ROOT))
    summary["ok"].append(f"{name} ({count})")


def fetch_and_save(name, path, params=None):
    data = get_json(path, params)
    if data is None:
        summary["failed"].append(name)
        return None
    save(name, data)
    return data


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    started = datetime.now(timezone.utc)
    log.info("Sleeper fetch started (no API key required)")

    # 1. Season/week. Missing fields fall back to safe defaults instead of crashing.
    state = fetch_and_save("state_nfl", "/state/nfl") or {}
    season = state.get("season") or str(started.year)
    week = state.get("week") or state.get("display_week") or 1
    log.info("season=%s week=%s", season, week)

    # 2. Trending players. PAGINATION: Sleeper has no pages/cursors; the only size
    #    control here is ?limit= (default 25), so one call returns everything we want.
    for kind in ("add", "drop"):
        fetch_and_save(f"trending_{kind}", f"/players/nfl/trending/{kind}",
                       params={"lookback_hours": 24, "limit": 50})

    # 3. Full player dictionary (~5 MB, one response, no paging). The docs ask us to
    #    call it at most once per day, so reuse today's file if it is fresh.
    players_file = RAW_DIR / "players_all.json"
    age_h = (time.time() - players_file.stat().st_mtime) / 3600 if players_file.exists() else None
    if age_h is not None and age_h < PLAYERS_MAX_AGE_HOURS:
        log.info("players_all.json is %.1f h old; skipping (once-per-day rule)", age_h)
        summary["skipped"].append("players_all (cached < 24h)")
    else:
        players = fetch_and_save("players_all", "/players/nfl")
        if players:
            # Missing-field safety: count players lacking a position instead of crashing.
            no_pos = sum(1 for p in players.values() if isinstance(p, dict) and not p.get("position"))
            if no_pos:
                log.warning("%d players have no 'position' field", no_pos)

    # 4. League data (optional). PAGINATION: league endpoints return the whole list in
    #    one response; "batching" is by week, so we loop over weeks ourselves.
    if not LEAGUE_ID:
        log.info("SLEEPER_LEAGUE_ID not set in .env; skipping league endpoints")
        summary["skipped"].append("league data (no SLEEPER_LEAGUE_ID)")
    else:
        fetch_and_save("league", f"/league/{LEAGUE_ID}")
        fetch_and_save("league_users", f"/league/{LEAGUE_ID}/users")
        rosters = fetch_and_save("league_rosters", f"/league/{LEAGUE_ID}/rosters") or []
        for r in rosters:
            if not r.get("owner_id"):
                log.warning("roster_id=%s has no owner_id (orphaned team)", r.get("roster_id", "?"))
        for wk in range(1, int(week) + 1):
            fetch_and_save(f"matchups_week_{wk:02d}", f"/league/{LEAGUE_ID}/matchups/{wk}")

    # Report what happened.
    secs = (datetime.now(timezone.utc) - started).total_seconds()
    log.info("-" * 60)
    log.info("Done in %.1fs  |  ok: %d  failed: %d  skipped: %d",
             secs, len(summary["ok"]), len(summary["failed"]), len(summary["skipped"]))
    for label in ("failed", "skipped"):
        for item in summary[label]:
            log.info("  %s: %s", label, item)
    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
