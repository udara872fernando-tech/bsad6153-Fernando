# Data Dictionary

## 1. Source
- **API Name:** Sleeper API[cite: 1]
- **Base URL:** `https://api.sleeper.app/v1/`[cite: 1]
- **Endpoints Used:** 
  - `/state/nfl` (NFL state / season info)
  - `/players/nfl/trending/add` and `/players/nfl/trending/drop` (Trending player additions/drops)
  - `/players/nfl` (Complete NFL player database)
  - `/league/<league_id>` (League metadata, rosters, users, matchups)[cite: 1]
- **Documentation:** [https://docs.sleeper.app/](https://docs.sleeper.app/)[cite: 1]
- **Authentication Method:** None required (Public, read-only API endpoints)[cite: 1].

---

## 2. What One Record Means
- **NFL State (`state_nfl`):** One record represents the current active state of the NFL league season (e.g., season year, active week, and season phase)[cite: 1].
- **Trending Players (`trending_add` / `trending_drop`):** One record represents a single NFL player who has been added or dropped in fantasy leagues over a specified lookback window, along with the total count of transactions[cite: 1].
- **Player Directory (`players_all`):** One entry represents a single active, retired, or historical NFL player or team defense, containing personal details, position, team affiliation, and status[cite: 1].
- **Matchups (`matchups`):** One record represents a single fantasy roster's performance and lineup scoring for a specific week[cite: 1].

---

## 3. Fields (Key Data Fields)

| Field Name | Data Type | Example Value | Description | Can Be Missing/Null? |
| :--- | :--- | :--- | :--- | :--- |
| `player_id` | String | `"4034"` | Unique identifier assigned to an NFL player or team defense. | No[cite: 1] |
| `first_name` | String | `"Patrick"` | Player's given first name. | Yes (for team defenses or null entries)[cite: 1] |
| `last_name` | String | `"Mahomes"` | Player's family last name. | Yes[cite: 1] |
| `position` | String | `"QB"` | Player's primary fantasy position (e.g., QB, RB, WR, TE). | Yes (240+ players lack position fields)[cite: 1] |
| `team` | String | `"KC"` | Abbreviation of the NFL team the player currently belongs to. | Yes (if player is a free agent)[cite: 1] |
| `status` | String | `"Active"` | Current professional player status. | Yes[cite: 1] |
| `count` | Integer | `1250` | Number of times a player was added or dropped in trending data. | No[cite: 1] |
| `season` | String | `"2026"` | The current active NFL season year. | No[cite: 1] |
| `week` | Integer | `8` | The current active week of the NFL season. | No[cite: 1] |
| `roster_id` | Integer | `1` | Unique identifier for a roster within a specific fantasy league. | No[cite: 1] |
| `points` | Float | `112.45` | Total fantasy points scored by a roster in a given week. | Yes[cite: 1] |

---

## 4. Identifiers and Relationships
- **Unique Identifier:** `player_id` uniquely identifies each player or team entity across all endpoints[cite: 1].
- **Relationships:**
  - `player_id` in the `trending_add` and `trending_drop` endpoints links directly to `player_id` in `players_all.json` to resolve full player details (name, team, position)[cite: 1].
  - `roster_id` in `matchups` links to `roster_id` in `league_rosters`[cite: 1].
  - `owner_id` on a roster links to `user_id` in `league_users`[cite: 1].

---

## 5. Update Behavior
- **Data Refresh Rates:**
  - `/state/nfl` updates weekly/daily as the season progresses[cite: 1].
  - Trending endpoints update dynamically every 24 hours based on league transactions[cite: 1].
  - `/players/nfl` is updated daily by Sleeper (the fetch script checks file age and updates once every 24 hours)[cite: 1].
- **Detecting New Data:** We detect new data by checking time-stamps on cached files or comparing newly fetched `player_id` keys against existing records in our database[cite: 1].

---

## 6. Surprises
1. **Missing Position Fields:** Approximately 240 player records in `/players/nfl` completely lack a `position` field, requiring safe `dict.get()` handling to prevent runtime crashes[cite: 1].
2. **200 OK Null Responses:** When querying an unknown or invalid ID, Sleeper returns an HTTP status code `200 OK` with a JSON body of `null` rather than a standard `404 Not Found` status code[cite: 1].
3. **Large Single Payload:** The full player dictionary (`/players/nfl`) is a single massive JSON response (~5 MB with over 12,000 records) without pagination, requiring caching logic to prevent redundant downloads[cite: 1].

---

## 7. Data-Use Ethics Check
- **Terms of Service Allow/Forbid:** Sleeper allows free, public read-only access to public endpoints without API keys, but forbids high-frequency spamming (>1,000 calls/min) and requires public attribution when launching a public application[cite: 1].
- **Real Identifiable People:** The data describes real, professional NFL athletes and public fantasy football participants[cite: 1]. As public sports figures and fantasy league players, this statistics data is publicly available and expected to be aggregated[cite: 1].
- **Worst Realistic Harm:** If stored data leaks or is misread, the worst harm would be displaying inaccurate fantasy projections/scores or wasting local disk storage; no sensitive private credentials, emails, or financial information are stored[cite: 1].
- **Access Control:** The local raw data and pipeline scripts should be writable only by system administrators/developers, while read access can be granted to the downstream web app and analytical modules[cite: 1].
