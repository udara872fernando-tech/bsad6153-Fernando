import json
import os
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set.")
    return psycopg2.connect(DATABASE_URL)


def load_data():
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        # --- 1. LOAD ACTIVE PLAYERS (No Duplicates) ---
        print("Loading active players...")
        players_path = os.path.join("data", "raw", "players_all.json")
        if os.path.exists(players_path):
            with open(players_path, "r", encoding="utf-8") as f:
                players_data = json.load(f)

            player_records = []
            for p_id, p in players_data.items():
                if p.get("active") is True:
                    player_records.append((
                        p_id,
                        p.get("first_name"),
                        p.get("last_name"),
                        p.get("position"),
                        p.get("team"),
                        json.dumps(p),
                    ))

            insert_players_sql = """
                INSERT INTO players (player_id, first_name, last_name, position, team, raw)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (player_id) DO NOTHING;
            """

            batch_size = 500
            for i in range(0, len(player_records), batch_size):
                batch = player_records[i : i + batch_size]
                cur.executemany(insert_players_sql, batch)
                conn.commit()

            print(f"Processed {len(player_records)} active players (duplicates skipped).")

        # --- 2. LOAD ROSTERS (No Duplicates) ---
        print("Loading rosters...")
        rosters_path = os.path.join("data", "raw", "rosters.json")
        if os.path.exists(rosters_path):
            with open(rosters_path, "r", encoding="utf-8") as f:
                rosters_data = json.load(f)

            roster_records = []
            for r in rosters_data:
                settings = r.get("settings", {})
                roster_records.append((
                    r.get("roster_id"),
                    r.get("league_id"),
                    r.get("owner_id"),
                    settings.get("wins", 0),
                    settings.get("losses", 0),
                    json.dumps(r),
                ))

            insert_rosters_sql = """
                INSERT INTO rosters (roster_id, league_id, owner_id, wins, losses, raw)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (roster_id) DO NOTHING;
            """
            cur.executemany(insert_rosters_sql, roster_records)
            conn.commit()
            print(f"Processed {len(roster_records)} rosters (duplicates skipped).")

        # --- 3. LOAD PLAYER STATS (UPSERT on conflict) ---
        print("Loading player stats...")
        stats_path = os.path.join("data", "raw", "player_stats.json")
        if os.path.exists(stats_path):
            with open(stats_path, "r", encoding="utf-8") as f:
                stats_data = json.load(f)

            stat_records = []
            for s in stats_data:
                stat_records.append((
                    s.get("player_id"),
                    s.get("roster_id"),
                    s.get("week"),
                    str(s.get("season")),
                    s.get("points"),
                    json.dumps(s),
                ))

            insert_stats_sql = """
                INSERT INTO player_stats (player_id, roster_id, week, season, points, raw)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (player_id, roster_id, week, season)
                DO UPDATE SET
                    points = EXCLUDED.points,
                    raw = EXCLUDED.raw;
            """
            cur.executemany(insert_stats_sql, stat_records)
            conn.commit()
            print(f"Processed {len(stat_records)} player stats (UPSERT complete).")

        print("Data loading completed successfully without duplicates!")

    except Exception as e:
        if conn is not None:
            conn.rollback()
        print(f"Error loading data: {e}", file=sys.stderr)
        raise

    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    load_data()