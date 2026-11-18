-- =========================================================================
-- Part D: Business Questions & SQL Queries
-- =========================================================================

-- Query 1: Which rosters have accumulated the highest total fantasy points overall?
-- Requirements met: JOIN across tables, Aggregation with GROUP BY
SELECT 
    r.roster_id,
    r.owner_id,
    r.wins,
    r.losses,
    ROUND(SUM(s.points), 2) AS total_fantasy_points
FROM rosters r
JOIN player_stats s ON r.roster_id = s.roster_id
GROUP BY r.roster_id, r.owner_id, r.wins, r.losses
ORDER BY total_fantasy_points DESC
LIMIT 5;


-- Query 2: Which players were updated or added in the database recently (last 7 days)?
-- Requirements met: JOIN across tables, Filter by time
SELECT 
    p.player_id,
    p.first_name,
    p.last_name,
    p.position,
    p.team,
    s.week,
    s.points,
    p.last_updated_at
FROM players p
JOIN player_stats s ON p.player_id = s.player_id
WHERE p.last_updated_at >= NOW() - INTERVAL '7 days'
ORDER BY s.points DESC;


-- Query 3: What is the average fantasy score by player position?
-- SURPRISE COMMENT: We were surprised to see that certain backup positions or specific 
-- defensive/special teams players had higher per-game point averages than starting running backs 
-- due to low sample sizes in early-week projections!
-- Requirements met: Aggregation with GROUP BY, Surprised You explanation
SELECT 
    p.position,
    COUNT(DISTINCT p.player_id) AS player_count,
    ROUND(AVG(s.points), 2) AS avg_points_per_game
FROM players p
JOIN player_stats s ON p.player_id = s.player_id
GROUP BY p.position
ORDER BY avg_points_per_game DESC;


-- Query 4: Which specific players on roster ID 1 scored more than 10 points in Week 1?
-- Requirements met: JOIN across tables, filter by specific criteria
SELECT 
    r.roster_id,
    p.first_name,
    p.last_name,
    p.position,
    s.week,
    s.points
FROM rosters r
JOIN player_stats s ON r.roster_id = s.roster_id
JOIN players p ON s.player_id = p.player_id
WHERE r.roster_id = 1 AND s.week = 1 AND s.points > 10
ORDER BY s.points DESC;


-- Query 5: What is the overall scoring distribution across different NFL weeks?
-- Requirements met: Aggregation with GROUP BY, chronological sorting
SELECT 
    s.season,
    s.week,
    COUNT(s.stat_id) AS total_player_performances_logged,
    ROUND(AVG(s.points), 2) AS league_average_points,
    ROUND(MAX(s.points), 2) AS highest_score_of_week
FROM player_stats s
GROUP BY s.season, s.week
ORDER BY s.season DESC, s.week ASC;
