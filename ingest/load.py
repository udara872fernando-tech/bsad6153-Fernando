import os
import json
import psycopg2
from dotenv import load_dotenv

# Load database URL from environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def load_data():
    conn = get_connection()
    cur = conn.cursor()

    try:
        # --- 1. LOAD PLAYERS (Parent Table) ---
        print("Loading players...")
        players_path = os.path.join("data", "players.json")  # adjust filename if needed
        if os.path.exists(players_path):
            with open(players_path, "r", encoding="utf-8") as f:
                players_data = json.load(f)

            # Sleeper API players dict format: { "player_id": { ...data... } }
            player_records = []
            for p_id, p in players_data.items():
                player_records.append((
                    p_id,
                    p.get("first_name"),
                    p.get("last_name"),
                    p.get("position"),
                    p.get("team"),
                    json.dumps(p)  # Raw JSON for jsonb column
                ))

            insert_players_sql = """
                INSERT INTO players (player_id, first_name, last_name, position, team, raw)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (player_id) DO NOTHING;
            """
            cur.executemany(insert_players_sql, player_records)
            print(f"Loaded {len(player_records)} players (or skipped duplicates).")

        # --- 2. LOAD ROSTERS (Parent Table) ---
        print("Loading rosters...")
        rosters_path = os.path.join("data", "rosters.json")  # adjust filename if needed
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
                    json.dumps(r)
                ))

            insert_rosters_sql = """
                INSERT INTO rosters (roster_id, league_id, owner_id, wins, losses, raw)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (roster_id) DO NOTHING;
            """
            cur.executemany(insert_rosters_sql, roster_records)
            print(f"Loaded {len(roster_records)} rosters (or skipped duplicates).")

        # --- 3. LOAD PLAYER STATS (Child Table) ---
        print("Loading player stats...")
        stats_path = os.path.join("data", "player_stats.json")  # adjust filename if needed
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
                    json.dumps(s)
                ))

            insert_stats_sql = """
                INSERT INTO player_stats (player_id, roster_id, week, season, points, raw)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (stat_id) DO NOTHING;
            """
            cur.executemany(insert_stats_sql, stat_records)
            print(f"Loaded {len(stat_records)} player stats (or skipped duplicates).")

        conn.commit()
        print("Data loading completed successfully!")

    except Exception as e:
        conn.rollback()
        print(f"Error loading data: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    load_data()