-- ============================================================================
-- Part E: Data Quality Checks (2026-11-22)
-- Run each query against PostgreSQL and record the result + date in docs/data_quality.md
-- ============================================================================

-- 1. Row counts per table
SELECT 'players' AS table_name, COUNT(*) AS row_count FROM players
UNION ALL
SELECT 'rosters' AS table_name, COUNT(*) AS row_count FROM rosters
UNION ALL
SELECT 'player_stats' AS table_name, COUNT(*) AS row_count FROM player_stats;

-- 2. Null rates for key fields
SELECT
    COUNT(*) AS total_players,
    COUNT(*) FILTER (WHERE first_name IS NULL OR last_name IS NULL) AS null_name_count,
    ROUND(100.0 * COUNT(*) FILTER (WHERE first_name IS NULL OR last_name IS NULL) / NULLIF(COUNT(*), 0), 2) AS null_name_pct,
    COUNT(*) FILTER (WHERE position IS NULL) AS null_position_count,
    ROUND(100.0 * COUNT(*) FILTER (WHERE position IS NULL) / NULLIF(COUNT(*), 0), 2) AS null_position_pct,
    COUNT(*) FILTER (WHERE team IS NULL) AS null_team_count,
    ROUND(100.0 * COUNT(*) FILTER (WHERE team IS NULL) / NULLIF(COUNT(*), 0), 2) AS null_team_pct
FROM players;

SELECT
    COUNT(*) AS total_stats,
    COUNT(*) FILTER (WHERE points IS NULL) AS null_points_count,
    ROUND(100.0 * COUNT(*) FILTER (WHERE points IS NULL) / NULLIF(COUNT(*), 0), 2) AS null_points_pct
FROM player_stats;

-- 3a. Duplicate check by natural/composite key
SELECT player_id, COUNT(*) AS cnt
FROM players
GROUP BY player_id
HAVING COUNT(*) > 1;

SELECT player_id, roster_id, week, season, COUNT(*) AS cnt
FROM player_stats
GROUP BY player_id, roster_id, week, season
HAVING COUNT(*) > 1;

-- 3b. "Same thing, different ID" check (e.g., same full name & position with multiple player_ids)
SELECT LOWER(TRIM(first_name)) AS norm_first,
       LOWER(TRIM(last_name)) AS norm_last,
       position,
       COUNT(DISTINCT player_id) AS distinct_ids,
       ARRAY_AGG(player_id) AS player_ids
FROM players
WHERE first_name IS NOT NULL AND last_name IS NOT NULL
GROUP BY LOWER(TRIM(first_name)), LOWER(TRIM(last_name)), position
HAVING COUNT(DISTINCT player_id) > 1;

-- 4. Out-of-range or inconsistent values (negative wins/losses/points or invalid week)
SELECT COUNT(*) AS negative_record_rosters
FROM rosters
WHERE wins < 0 OR losses < 0;

SELECT COUNT(*) AS invalid_week_or_negative_points
FROM player_stats
WHERE week < 0 OR week > 22 OR points < 0;

-- 5. Orphan checks (child records missing parent)
SELECT COUNT(*) AS orphan_stats_missing_player
FROM player_stats ps
LEFT JOIN players p ON ps.player_id = p.player_id
WHERE p.player_id IS NULL;

SELECT COUNT(*) AS orphan_stats_missing_roster
FROM player_stats ps
LEFT JOIN rosters r ON ps.roster_id = r.roster_id
WHERE r.roster_id IS NULL;

-- 7. Fairness check: distribution across positions or teams (shows representation skew)
SELECT COALESCE(position, 'UNKNOWN') AS position_group,
       COUNT(*) AS player_count,
       ROUND(100.0 * COUNT(*) / NULLIF((SELECT COUNT(*) FROM players), 0), 2) AS pct_of_players
FROM players
GROUP BY COALESCE(position, 'UNKNOWN')
ORDER BY player_count DESC;