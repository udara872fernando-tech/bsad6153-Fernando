1 | # Database Schema Design (`docs/schema.md`)
 2 | 
 3 | ## Entity-Relationship Diagram
 4 | 
 5 | ```mermaid
 6 | erDiagram
 7 |     players {
 8 |         string player_id PK
 9 |         string first_name
10 |         string last_name
11 |         string position
12 |         string team
13 |         timestamptz first_seen_at
14 |         timestamptz last_updated_at
15 |         jsonb raw
16 |     }
17 | 
18 |     rosters {
19 |         int roster_id PK
20 |         string league_id
21 |         string owner_id
22 |         int wins
23 |         int losses
24 |         timestamptz first_seen_at
25 |         timestamptz last_updated_at
26 |         jsonb raw
27 |     }
28 | 
29 |     player_stats {
30 |         int stat_id PK
31 |         string player_id FK
32 |         int roster_id FK
33 |         int week
34 |         string season
35 |         numeric points
36 |         timestamptz first_seen_at
37 |         timestamptz last_updated_at
38 |         jsonb raw
39 |     }
40 | 
41 |     players ||--o{ player_stats : "generates stats for"
42 |     rosters ||--o{ player_stats : "contains"
43 | ```
44 | 
45 | ---
46 | 
47 | ## Table Descriptions
48 | 
49 | - **`players`**: Each row represents an individual NFL player fetched from the Sleeper API...
50 | - **`rosters`**: Each row represents a fantasy team roster within a specific league...
51 | - **`player_stats`**: Each row represents a single player's weekly performance metrics...
52 | 
53 | ---
54 | 
55 | ## Design Decision Justification
56 | 
57 | **Decision:** We debated whether to store player weekly performance statistics...
