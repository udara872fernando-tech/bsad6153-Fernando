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
}
```
