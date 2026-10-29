# docs/

Your project's written evidence. Each file is described on its week's Canvas page.

| Week | File |
|---|---|
| 1 | `data_dictionary.md`, `baseline_log.md` (template provided) |
| 2 | `schema.md` (ER diagram and access roles), `data_quality.md`, `implementation_brief.md` |
| 3 | `sync_tests.md` |
| 4 | `app_spec.md`, `code_tour.md`, `app_verification.md`, `peer_review.md`, `usage_log.md` (template provided) |
| 5 | `chatbot_rules.md`, `eval_week5.md` |
| 6 | `agent_design.md`, `agent_traces.md`, `user_test.md` |
| 7 | `eval_report.md`, `red_team.md`, `hardening.md`, `audit.md` |
| 8 | `business_case.md` |

Logs are research data: record entries when things happen, and never invent or adjust them.
## Project Proposal

### Data Source & Backup
This project utilizes the public **Sleeper API** (`https://api.sleeper.app/v1/`) as its primary data source to ingest active NFL season states, trending player adds/drops, and full player directory metadata without requiring API keys. As a backup data source in case of endpoint outages, the pipeline is designed to failover to public **ESPN Fantasy endpoints** (`site.api.espn.com`) or fallback to cached historical JSON payloads stored in `data/raw/`.

### Your Decision & Workflow
The core decision targeted by this system is optimizing weekly fantasy football roster management—specifically evaluating sit/start lineup decisions and priority waiver wire claims. Currently, this workflow requires manually cross-referencing multiple fragmented sources (Sleeper player news, injury reports, and target share statistics), taking upwards of 20 minutes per decision with mixed confidence. This system aims to automate data aggregation into a single unified pipeline, cutting decision time under 5 minutes while grounding recommendations in real-time transaction trends and player availability metrics.

### Agent Idea (First Draft)
By Week 6, the AI agent will function as an automated **Fantasy Roster Assistant**. Rather than simply answering static Q&A questions, the agent will actively ingest local raw JSON feeds (`data/raw/`), evaluate a user's roster against current trending player pickups, cross-reference injury designations, and generate an actionable weekly execution plan (e.g., "Recommend dropping Player X for Player Y due to a 35% surge in league-wide trending adds following an injury update").

### Risks
- **Rate Limits & API Blocks:** Sleeper caps API calls at ~1,000 requests per minute; excessive unthrottled requests risk temporary IP blocks.
- **Large Payload Overhead:** The primary player endpoint (`/players/nfl`) returns a single ~5 MB JSON object, requiring disk caching to avoid network bottlenecks.
- **Data Quality & Nulls:** Over 200 player records lack explicit position or team fields, requiring robust exception handling.
- **Terms of Service:** Public display requires attribution, and commercial resale is strictly prohibited.