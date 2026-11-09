# Database Schema Design (`docs/schema.md`)

## Entity-Relationship Diagram

```mermaid
erDiagram
    players {
        string player_id PK
        string first_name
        string last_name
        string position
        string team
        timestamptz first_seen_at
        timestamptz last_updated_at
        jsonb raw
    }

    rosters {
        int roster_id PK
        string league_id
        string owner_id
        int wins
        int losses
        timestamptz first_seen_at
        timestamptz last_updated_at
        jsonb raw
    }

    player_stats {
        int stat_id PK
        string player_id FK
        int roster_id FK
        int week
        string season
        numeric points
        timestamptz first_seen_at
        timestamptz last_updated_at
        jsonb raw
    }

    players ||--o{ player_stats : "generates stats for"
    rosters ||--o{ player_stats : "contains"
    
    Table Descriptions
players: Each row represents an individual NFL player fetched from the Sleeper API, storing core biographical data, positional metadata, and audit tracking.

rosters: Each row represents a fantasy team roster within a specific league, tracking owner associations and overall team performance records (wins/losses).

player_stats: Each row represents a single player's weekly performance metrics (such as fantasy points scored) for a specific NFL week and season.

Design Decision Justification
Decision: We debated whether to store player weekly performance statistics inside a flattened JSON column directly within the players table versus creating a normalized relational child table (player_stats).

Justification: We chose to normalize performance metrics into a separate player_stats table with explicit foreign keys (player_id and roster_id). While a JSON blob would have simplified initial data ingestion, a normalized relational design is necessary to efficiently answer multi-variable business queries (like aggregating top-scoring players across specific weeks and seasons) while still retaining a raw jsonb column on every table to safely capture unmodeled API metadata.