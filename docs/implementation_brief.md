# Implementation Brief: "Should This Use AI?"

---

## 1. Your Workflow
* **The Decision:** Which players to start in my weekly Fantasy Football lineup (WR/RB/TE/FLEX, QB, and Defense streaming spots) based on matchup metrics, projections, and injury reports.
* **Frequency:** Weekly during the NFL season (September–January), including mid-week waiver wire and matchup evaluations.
* **Current Tools & Steps:** I currently cross-reference Yahoo Fantasy newsletters, the Sleeper app trending lists, FantasyPros consensus rankings, Twitter/X beat writer reports, and injury update logs.
* **Time Spent:** 12 to 22 minutes per decision (average ~15–18 minutes; e.g., Oct 13 waiver wire took 18 mins, Oct 18 lineup took 22 mins, Oct 20 trade took 15 mins, Oct 25 RB injury check took 12 mins, and Oct 27 defense claim took 10 mins).
* **Frustrations:** 
  1. **Aggregating Fragmented Information:** Cross-referencing player news across multiple standalone apps and social media feeds takes significant manual effort (over 60% of decision time is spent just gathering scattered data).
  2. **Evaluating Injury Impact:** Determining how a sudden injury affects target share and volume for backup players across the roster.
  3. **Sifting Through Noise:** Filtering out biased opinions or outdated advice on Reddit and Twitter/X to find actionable data before game lock.

---

## 2. "Should This Use AI?"

| Option | Description | What it Solves | Estimated Cost | What Could Go Wrong |
| :--- | :--- | :--- | :--- | :--- |
| **A. No new technology** | A manual review checklist and a structured spreadsheet. | Organizes data sources into a single manual review workflow. | $0 (Time investment only) | High human error, tedious manual data entry, and still requires manually hunting down scattered injury news. |
| **B. Data without AI** | A Supabase PostgreSQL database and Streamlit dashboard displaying saved SQL reports of player stats, trending adds/drops, and matchup metrics. | Instantly queries and centralizes structured Sleeper API stats, projections, and matchup rankings in one view. | $0 (Free tier hosting on Render & Supabase) | Rigid SQL tables cannot synthesize unstructured context, weigh nuanced injury scenarios, or answer ad-hoc comparative lineup questions naturally. |
| **C. LLM chatbot and/or agent** | A tool-using LLM chatbot/agent (Milestones 5–6) connected to the Supabase database that synthesizes SQL stats with user queries to provide tailored start/sit recommendations. | Instantly compares multi-variable stats and explains trade-offs in plain language with cited statistical backing. | ~$5–$10/month in LLM API credits | Risk of hallucinating stats if not strictly grounded in database queries, or giving stale advice if the data sync is outdated. |

### Honest Technical Breakdown
* **What needs plain data & SQL (80%):** Ingesting Sleeper API endpoints (`state_nfl`, `trending_add`, `trending_drop`, `players_all`), storing structured player records in PostgreSQL, and filtering/ranking players by position, availability, and baseline metrics. Option B handles all deterministic data retrieval and sorting reliably without an LLM.
* **What actually needs an LLM (20%):** Acting as a conversational synthesis layer on top of those SQL results—translating multi-player statistical comparisons, injury context, and matchup trade-offs into concise, transparent start/sit reasoning tailored to my specific roster constraints.

---

## 3. Value Hypothesis
* **Outcome 1 (Time Efficiency):** Baseline decision time is **15–20 minutes** per lineup decision (measured 10–22 minutes in Milestone 1); target is **under 5 minutes** per decision.
* **Outcome 2 (Decision Confidence):** Baseline self-reported confidence score is **3/5** (ranging from 2 to 4 in the baseline log); target is **4/5 or higher**, supported by transparent statistical evidence.
* **Measurement Plan:** Starting with the usage log in Milestone 4, I will log the start-to-finish duration (in minutes), self-reported confidence rating (1–5), and whether the AI's cited metrics matched the underlying database records for every weekly lineup decision.

---

## 4. Early Cost Estimate
* **Infrastructure & Hosting:** **$0/month** — Supabase (PostgreSQL database, free tier), GitHub Actions (scheduled data sync, free for public repositories), and Render (Streamlit web service, free tier, sleeps when idle).
* **LLM API Usage:** Estimated at **$2–$5/month** during the active NFL season. Assuming ~15 queries per week (~60 queries/month) at ~$0.01–$0.03 per query using a lightweight model (e.g., Claude Haiku / GPT-4o-mini) with concise SQL context payloads, monthly spend stays well under $5.
* **Hard Spending Cap:** **$20 prepaid API credit limit** configured on the LLM provider account before Milestone 5, with **auto-reload turned off**.
* **Fallback When Cap Is Reached:** If the $20 credit limit is exhausted, the Streamlit app catches the API quota/billing error, disables the chat input box with a clear status banner, and falls back gracefully to the read-only SQL dashboard tables and saved views (Option B) so core data remains usable.

---

## 5. Risks and Governance
* **What happens if the system is wrong:** A flawed start/sit recommendation results in suboptimal fantasy points and potentially losing a weekly fantasy matchup. Financial and physical stakes are zero; the impact is strictly recreational.
* **Who could be harmed or misled:** Primarily me as the team manager. If shared publicly on Render, other visitors could see inaccurate fantasy advice if they treat it as guaranteed sports analysis rather than an experimental tool.
* **Data Privacy & Real People:** The database ingests public NFL player names, team affiliations, positions, and public Sleeper trending counts—no private user data, financial records, or personally identifiable information (PII) of private individuals is collected or exposed.
* **Hard Autonomous Limits (What the AI must NEVER do):**
  1. **Never submit or accept trade offers** on my behalf.
  2. **Never add, drop, or claim players** on waivers without explicit manual action by me.
  3. **Never modify or lock starting lineups** automatically—the agent operates strictly in read-only advisory mode.

---

## 6. Scorecard Self-Assessment (Version 1)

1. **Real user and workflow:** **Green** — Directly addresses my documented weekly fantasy football lineup and waiver wire decision workflow.
2. **Data access:** **Green** — Sleeper's public read-only JSON API requires no API key and reliably syncs player and trending data into Supabase.
3. **Data understanding:** **Yellow** — While core player and trending schemas are verified (including handling 240 records missing position fields), Sleeper's base endpoints lack deep snap-count and red-zone target metrics.
4. **Freshness and monitoring:** **Green** — Scheduled GitHub Actions workflows keep the PostgreSQL database updated automatically ahead of weekly game locks.
5. **Grounding:** **Yellow** — The LLM must be strictly constrained via read-only database tools so it cites actual database records rather than guessing player stats or injury statuses.
6. **Bounded autonomy:** **Green** — Database roles (`APP_DATABASE_URL` / `AGENT_DATABASE_URL`) and application rules enforce read-only behavior with zero roster-mutation permissions.
7. **Evaluation:** **Yellow** — Success criteria are defined via baseline logs, but automated golden-question evals (`evals/`) and post-game accuracy checks are not yet built.
8. **Measured value and cost:** **Green** — Free-tier hosting ($0) and a $20 prepaid API cap ensure benefits easily outweigh minimal operating costs.
9. **Adoption:** **Green** — Built specifically around my personal decision habits, reducing the >60% time overhead I currently spend gathering scattered information.
10. **Governance and accountability:** **Green** — Human-in-the-loop approval is mandatory for all roster moves, and a disclaimer clarifies the system's advisory limits.

### Plans for the Two Weakest Factors
* **Factor 3 (Data understanding):** *Plan:* Explicitly document missing fields and schema limitations in `docs/` and configure the system prompt to disclose when granular metrics (like snap counts or real-time beat-writer injury updates) are unavailable in the database so it never fabricates missing stats.
* **Factor 7 (Evaluation):** *Plan:* Build a set of 10–15 golden test questions in `evals/` covering common start/sit and injury edge cases, and log weekly pre-game recommendations against actual post-game fantasy points starting in Milestone 5 to measure grounding and accuracy objectively.