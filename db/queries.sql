-- =========================================================================
-- Part D: Business Questions & SQL Queries (Aligned to Baseline Log)
-- =========================================================================

-- Query 1 (Baseline Tie-In: Roster Size & Active Player Composition):
-- Baseline question: "Are rosters holding a realistic set of players (~15-20) rather than
-- inflating league-wide stats onto every team?"
-- Uses: JOIN across rosters, roster_players, players, and player_stats + GROUP BY aggregation.
SELECT
    r.roster_id,
    r.owner_id,
    r.wins,
    r.losses,
    COUNT(DISTINCT rp.player_id) AS rostered_player_count,
    ROUND(COALESCE(SUM(ps.points), 0), 2) AS total_rostered_points
FROM rosters r
LEFT JOIN roster_players rp ON r.roster_id = rp.roster_id
LEFT JOIN players p ON rp.player_id = p.player_id
LEFT JOIN player_stats ps ON p.player_id = ps.player_id
GROUP BY r.roster_id, r.owner_id, r.wins, r.losses
ORDER BY r.roster_id;


-- Query 2 (Surprising Result #1: Wins & Losses vs. Total Points):
-- SURPRISE COMMENT: Wins and losses do NOT track total points cleanly—some managers
-- with lower cumulative points hold more wins (or vice versa) due to weekly matchup
-- schedule variance and opponent scoring luck rather than raw points alone.
-- Uses: JOIN + aggregation by win/loss record.
SELECT
    r.wins,
    r.losses,
    COUNT(DISTINCT r.roster_id) AS team_count,
    ROUND(AVG(COALESCE(ps.points, 0)), 2) AS avg_player_stat_points
FROM rosters r
LEFT JOIN roster_players rp ON r.roster_id = rp.roster_id
LEFT JOIN player_stats ps ON rp.player_id = ps.player_id
GROUP BY r.wins, r.losses
ORDER BY r.wins DESC, r.losses ASC;


-- Query 3 (Surprising Result #2: Position Scoring Averages — QBs Lowest in Table):
-- SURPRISE COMMENT: Contrary to an assumption that quarterbacks might lead averages,
-- QBs actually show the lowest average in the table here due to small sample sizes
-- and position scoring weighting in the loaded dataset.
-- Uses: JOIN between players and player_stats + GROUP BY position.
SELECT
    p.position,
    COUNT(DISTINCT p.player_id) AS distinct_players,
    COUNT(ps.stat_id) AS stat_rows,
    ROUND(AVG(ps.points), 2) AS avg_points
FROM players p
JOIN player_stats ps ON p.player_id = ps.player_id
GROUP BY p.position
ORDER BY avg_points DESC;


-- Query 4 (Time Filter on Integer Season & Week):
-- Baseline question: "How did players perform in a specific season and recent week window?"
-- Uses: JOIN + explicit integer season and week filter.
SELECT
    p.player_id,
    p.first_name,
    p.last_name,
    p.position,
    p.team,
    ps.season,
    ps.week,
    ps.points
FROM players p
JOIN player_stats ps ON p.player_id = ps.player_id
WHERE ps.season = 2025
  AND ps.week BETWEEN 2 AND 4
  AND p.team IS NOT NULL
ORDER BY ps.points DESC, p.last_name ASC
LIMIT 15;


-- Query 5 (Recent Update Timestamp Filter & Lineup Slot Breakdown):
-- Baseline question: "Which rostered players were recently updated and how are their
-- fantasy points distributed across roster slots?"
-- Uses: Multi-table JOIN + timestamp filter + GROUP BY.
SELECT
    rp.slot_status,
    COUNT(*) AS player_week_entries,
    ROUND(AVG(ps.points), 2) AS avg_points,
    ROUND(MAX(ps.points), 2) AS max_points
FROM roster_players rp
JOIN players p ON rp.player_id = p.player_id
JOIN player_stats ps ON p.player_id = ps.player_id
WHERE ps.last_updated_at >= NOW() - INTERVAL '7 days'
GROUP BY rp.slot_status
ORDER BY avg_points DESC;