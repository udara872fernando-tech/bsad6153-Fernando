-- =========================================================================
-- Relational Schema: Core Entities, Constraints & Pipeline Observability
-- =========================================================================

CREATE TABLE IF NOT EXISTS players (
    player_id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL DEFAULT 'Unknown',
    last_name TEXT NOT NULL DEFAULT 'Unknown',
    position TEXT NOT NULL DEFAULT 'UNK'
        CHECK (position IN ('QB', 'RB', 'WR', 'TE', 'K', 'DEF', 'DL', 'LB', 'DB', 'IDP', 'UNK')),
    team TEXT CHECK (team IS NULL OR char_length(TRIM(team)) BETWEEN 2 AND 4),
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    raw JSONB NOT NULL DEFAULT '{}'::jsonb,
    last_updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS rosters (
    roster_id INTEGER PRIMARY KEY CHECK (roster_id > 0),
    league_id TEXT NOT NULL,
    owner_id TEXT NOT NULL,
    wins INTEGER NOT NULL DEFAULT 0 CHECK (wins >= 0),
    losses INTEGER NOT NULL DEFAULT 0 CHECK (losses >= 0),
    raw JSONB NOT NULL DEFAULT '{}'::jsonb,
    last_updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Many-to-many join table between rosters and players (~15-20 players per roster)
CREATE TABLE IF NOT EXISTS roster_players (
    roster_id INTEGER NOT NULL REFERENCES rosters(roster_id) ON DELETE CASCADE,
    player_id TEXT NOT NULL REFERENCES players(player_id) ON DELETE CASCADE,
    slot_status TEXT NOT NULL DEFAULT 'bench'
        CHECK (slot_status IN ('starter', 'bench', 'ir', 'taxi')),
    last_updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (roster_id, player_id)
);

CREATE TABLE IF NOT EXISTS player_stats (
    stat_id SERIAL PRIMARY KEY,
    player_id TEXT NOT NULL REFERENCES players(player_id) ON DELETE CASCADE,
    week INTEGER NOT NULL CHECK (week BETWEEN 1 AND 18),
    season INTEGER NOT NULL CHECK (season BETWEEN 2020 AND 2030),
    points NUMERIC(8, 2) NOT NULL DEFAULT 0.00 CHECK (points >= -10.00),
    raw JSONB NOT NULL DEFAULT '{}'::jsonb,
    last_updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (player_id, week, season)
);

-- Ensure existing tables have last_updated_at if created earlier without it
ALTER TABLE players ADD COLUMN IF NOT EXISTS last_updated_at TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE rosters ADD COLUMN IF NOT EXISTS last_updated_at TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE player_stats ADD COLUMN IF NOT EXISTS last_updated_at TIMESTAMPTZ DEFAULT NOW();

-- Pipeline run audit log
CREATE TABLE IF NOT EXISTS sync_runs (
    run_id SERIAL PRIMARY KEY,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    status TEXT NOT NULL CHECK (status IN ('success', 'partial', 'failed')),
    records_fetched INTEGER NOT NULL DEFAULT 0 CHECK (records_fetched >= 0),
    records_inserted INTEGER NOT NULL DEFAULT 0 CHECK (records_inserted >= 0),
    records_updated INTEGER NOT NULL DEFAULT 0 CHECK (records_updated >= 0),
    error_message TEXT,
    trigger TEXT NOT NULL CHECK (trigger IN ('schedule', 'manual'))
);

CREATE INDEX IF NOT EXISTS idx_players_team ON players(team);
CREATE INDEX IF NOT EXISTS idx_roster_players_player ON roster_players(player_id);
CREATE INDEX IF NOT EXISTS idx_player_stats_season_week ON player_stats(season, week);