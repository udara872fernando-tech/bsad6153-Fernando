## The Finding

- When fetching the full NFL player dictionary, the ingestion logs explicitly capture that 240 players have no'position'field.

## The Fairness/Bias Check

- If an AI agent or automated recommendation model builds player tier lists or waiver-wire rankings, an uncritical assumption that all records have a valid position introduces a positional inclusion bias. The model implicitly treats unassigned or fringe players and anomalies, filtering them out entirely or misattributing their value.

## Systemic Blind Spots & Unfair Exclusion

- If the AI agent is tasked with recommending sleeper picks across all roster types, blindly trusting the raw dataset without handling missing position tags will cause the agent to completely ignore these 240 players. This creates a skewed, unfair evaluation framework that exclusively prioritizes established offensive skill position while rendering fringe or emerging talent invisible.

## Pipeline Crashes or Silent Corrupt Output

- If an autonomous agent runs a scoring script that groups player metrics by position without a guard for none or missing keys, the script will throw a TypeError or KeyError. Alternatively, if the agent uses a naive imputation strategy it will pollute position-specific analytics, resulting in nonsensical AI recommendations. 

## Data Quality Report (2026-11-22)

All measurements below were collected on **2026-11-22** using the queries in `db/quality_checks.sql`.

### 1. Row Counts per Table
- `players`: **9,422** rows (`2026-11-22`)
- `rosters`: **10** rows (`2026-11-22`)
- `player_stats`: **9,423** rows (`2026-11-22`)

### 2. Null Rates for Key Fields
- `players` missing name (`first_name` or `last_name` is NULL): **0** / **0.00%** out of **9,422** players (`2026-11-22`)
- `players` missing `position`: **32** / **0.34%** out of **9,422** players (`2026-11-22`)
- `players` missing `team`: **6,680** / **70.90%** out of **9,422** players (`2026-11-22`)
- `player_stats` missing `points`: **0** / **0.00%** out of **9,423** rows (`2026-11-22`)

### 3. Duplicate Checks
- **By primary / natural / composite key:** **0** duplicate `player_id` groups in `players` and **0** duplicate `(player_id, roster_id, week, season)` groups in `player_stats` (`2026-11-22`)
- **"Same thing, different ID":** **18** normalized `first_name + last_name + position` combinations appear with **2** distinct `player_id`s each (for example, `caleb johnson` `LB` with `['11303', '7846']` and `chase cota` `WR` with `['11347', '11554']`) (`2026-11-22`)

### 4. Out-of-Range or Inconsistent Values
- `rosters` with negative `wins` or `losses`: **0** (`2026-11-22`)
- `player_stats` with out-of-range `week` (`< 0` or `> 22`) or negative `points`: **0** (`2026-11-22`)

### 5. Orphan Records
- `player_stats` missing a matching `players.player_id`: **0** (`2026-11-22`)
- `player_stats` missing a matching `rosters.roster_id`: **0** (`2026-11-22`)
- **How our design handles orphans:** `load.py` loads `players` and `rosters` before `player_stats` and uses `ON CONFLICT DO NOTHING` on `players` and `rosters` and `ON CONFLICT (player_id, roster_id, week, season) DO UPDATE` on `player_stats` so idempotent upserts stay consistent without creating duplicate records

### 6. Decisions (Cleaned, Rejected, Left Alone)
- **Filtered / upserted on ingest:** `load.py` filters `players_all.json` to `active is True` before inserting into `players`, skips duplicate primary keys (`ON CONFLICT DO NOTHING`) for `players` and `rosters`, and updates `points` and `raw` on conflict (`ON CONFLICT DO UPDATE`) for `player_stats`[cite: 2].
- **Left alone:** We left `team` `NULL` values (**6,680** rows / **70.90%** on `2026-11-22`) and `position` `NULL` values (**32** rows / **0.34%** on `2026-11-22`) untouched rather than guessing or fabricating team/position labels, and we kept duplicate-name `player_id` pairs distinct rather than merging IDs automatically without verifying whether they represent different players or ID migrations.

### 7. Fairness Check
- **Measurement (`2026-11-22`):** Across **9,422** players, **WR** is the largest group with **1,365** players (**14.49%**), while **6,680** players (**70.90%**) have `team IS NULL`, **32** (**0.34%**) have `NULL` position, **32** (**0.34%**) are `UNKNOWN`, and **1** (`K/P`) is **0.01%**
- **Risk & why it matters:** If a future chatbot filters or groups by `team` or assumes every player has a current team assignment, **70.90%** of player records (`2026-11-22`) with `NULL` `team` would be omitted or mischaracterized—leading to misleading team comparisons or unsupported claims about a player's current roster/team status. The chatbot should report when `team` is missing or decline questions requiring unrecorded team assignments.