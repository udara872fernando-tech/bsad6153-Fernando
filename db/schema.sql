-- 1. Ensure data tables track when a record actually changes (Part B)
ALTER TABLE players ADD COLUMN IF NOT EXISTS last_updated_at TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE rosters ADD COLUMN IF NOT EXISTS last_updated_at TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE player_stats ADD COLUMN IF NOT EXISTS last_updated_at TIMESTAMPTZ DEFAULT NOW();

-- 2. Create the sync_runs logging table (Part C)
CREATE TABLE IF NOT EXISTS sync_runs (
    run_id SERIAL PRIMARY KEY,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    status TEXT NOT NULL CHECK (status IN ('success', 'partial', 'failed')),
    records_fetched INTEGER DEFAULT 0,
    records_inserted INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    error_message TEXT,
    trigger TEXT NOT NULL CHECK (trigger IN ('schedule', 'manual'))
);
