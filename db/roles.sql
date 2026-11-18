-- db/roles.sql
-- Read-only role for golden-question checker, web app, and chatbot
CREATE ROLE app_reader LOGIN;

GRANT USAGE ON SCHEMA public TO app_reader;
GRANT SELECT ON players, rosters, player_stats, sync_runs TO app_reader;