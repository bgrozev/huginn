# Huginn — implementation plan (v2: hosted, scheduled)

Huginn (Odin's raven, "thought") flies out, gathers weather, comes back with an assessment.
v1 was a local Claude skill (`weather-flying/`) producing one HTML file per run.
v2 runs unattended on GitHub, publishes to **https://huginn.mustelinae.net**.

## Goals

- Predefined spots, grouped (first group: **Salt Lake City Area** — POM South, POM North, Cherry).
- One activity per report. **Speedflying only** for now; structure allows paragliding later.
- Forecast horizon: 3 days × AM/PM = **6 slots**, rolling from the run time.
- Nearest slot also uses **current observations**, later slots are forecast-only.
- Runs **twice daily**, unattended. Every run archived — history is a first-class feature.
- Mobile-first (glance before driving to launch), desktop for deep dives.
- Purpose is learning: every call must show *why*, with links to the source charts.

## Non-goals (for now)

Databases, servers, accounts, paragliding, user-tunable thresholds, push notifications.

## Architecture

```
GitHub Actions (cron 2×/day)
  1. fetch   — Python, deterministic: NWS AFD, gridpoint forecast, winds aloft, TAF, station obs
               → raw/<run-id>.json  (archived, never edited)
  2. assess  — Claude agent reads knowledge/ + spots/ + raw JSON
               → report JSON (chance, rating, checks, warnings, explanation per spot × slot)
  3. validate — JSON schema + sanity rules (kt only, every slot present, links resolve)
  4. publish — commit site/reports/<run-id>.json, update index.json + latest.json, deploy Pages
```

Three things kept separate (from the design discussion — makes it auditable and debuggable):

| Layer | What | Who produces it |
|---|---|---|
| Raw data | Forecast values, obs, AFD text, source URLs | Python fetchers |
| Assessment | Rule checks (direction in range, speed under max, aloft rotor triggers) → pass/warn/fail | Rules from spot files; agent applies them, later a Python rules engine |
| Explanation | Plain-language reasoning, chance %, what to watch | Claude |

The AI explains the rules, it does not invent them. Thresholds live in spot/knowledge files under
version control. Feedback never changes thresholds automatically.

### Single workflow, not two

Commits pushed with `GITHUB_TOKEN` do **not** trigger other workflows. So the scheduled workflow
builds and deploys Pages itself (`actions/upload-pages-artifact` + `actions/deploy-pages`) after
committing the report. A separate `push`-triggered deploy workflow handles template/knowledge edits.

### Agent runtime

Option A (recommended): `anthropics/claude-code-action` in headless mode with a fixed prompt file
(`agent/prompt.md`), tools restricted to Read/Write + WebFetch on an allowlist of weather domains.
Option B: Python + Claude Agent SDK. Start with A — least code; move to B if we need tighter control.

Secret: `CLAUDE_CODE_OAUTH_TOKEN` (Claude subscription) in repo secrets. Model: latest Opus.

### Schedule

Once a day at 14:00 Utah time: today's afternoon uses midday observations and shows whether the
diurnal switch happened; the next days' mornings are ready the evening before. Cron is UTC without
DST, so 20:00 and 21:00 UTC are both scheduled and a gate job keeps the one that is 14:00 in
America/Denver. Plus `workflow_dispatch` for manual runs.

## Repo layout

```
PLAN.md                     this file
knowledge/weather.md        how the air works, data sources (any activity, any area)
knowledge/speedflying.md    what the weather means for a speedflyer (ratings consequences)
knowledge/reporting.md      ratings, chance %, warnings, wording
spots/<group>/_group.md     group/area knowledge: WFO, diurnal pattern, obs stations
spots/<group>/<spot>.md     YAML front matter (machine-readable) + local knowledge prose
schema/report.schema.json   report contract between agent and site
site/                       static site deployed to Pages
  index.html                overview: map + spots×slots table + detail panel
  assets/                   css, js renderer
  reports/index.json        history list
  reports/latest.json       copy of newest report
  reports/<run-id>.json     one per run
agent/prompt.md             (phase 2) agent instructions
scripts/                    (phase 2) fetchers, validator
.github/workflows/          (phase 2/3) deploy + scheduled run
weather-flying/             v1 skill (legacy, local only — not committed yet)
```

## Report contract (schema v1, summary)

`site/reports/<run-id>.json` — see `schema/report.schema.json`.

- `generated_at` (UTC ISO), `timezone`, `activity`, `run` (trigger, model, commit)
- `slots[6]`: id, date, part (`am`|`pm`), label, `basis` (`forecast+obs`|`forecast`)
- `groups[]`: id, name, `synoptic` (summary, pressure, afd excerpt, links), `observations[]`
  - `spots[]`: id, name, lat/lon, faces, `cells{slot_id → cell}`
    - cell: `chance` (0–100, est. chance conditions meet the spot's criteria — not AI confidence),
      `rating` (go/marginal/nogo/unknown), `confidence` (data quality), `window`, `headline`,
      `wind` (launch estimate + aloft levels), `checks[]` (rule, result, detail),
      `warnings[]` (severity, title, why, triggered_by, investigate), `explanation`, `sources[]`
- `sources[]`: every fetched URL with fetch time and ok flag

## Site (templates)

- **Header**: report time (local + "x hours ago", stale banner > 14 h), activity, disclaimer link.
- **Group tabs** (one group now, built for many).
- **Map** (Leaflet + OSM) with pins coloured by next-slot rating; tap → scroll to row.
- **Table**: rows = spots, columns = 6 slots; cell = chance % on rating colour; sticky first column,
  horizontal scroll on phones.
- **Detail panel** (cell tap): rating, window, wind at launch + aloft, rule checks, warnings
  (educational: why it fired, which data, what to look for), explanation, source links.
- **Group synoptic** card: pattern, pressure, AFD quote, links; obs chips for the nearest slot.
- **History**: list from `index.json`; `?r=<run-id>` permalinks any past run.
- **Disclaimer / assumption of risk**: always visible footer + first-visit acknowledgement.

## Phases

1. **Foundations** (this iteration) — repo, Pages + custom domain, knowledge extraction,
   spot files, report schema, site templates rendered against a sample report.
2. **Agent** — fetch scripts, agent prompt, validator; run locally end to end; manual
   `workflow_dispatch` on Actions; compare to v1 skill output.
3. **Schedule** — cron 2×/day, history index, stale-report banner, failure notification
   (issue opened on failed run).
4. **Trust** — Python rules engine computes `checks` deterministically (agent only explains);
   post-flight feedback (GitHub issue form per spot/slot: flew? matched forecast? surprises?);
   forecast-vs-actual review.
5. **Grow** — more groups/spots, paragliding activity, model comparison (HRRR/NAM/GFS),
   tag filters (e.g. north-facing).

## Open questions

- Speed thresholds: POM South lists "speed/mini ideal 14–17 kt, max 22 kt"; POM North lists P2/M1
  (paragliding) numbers; Cherry has no number. Need speedflying-specific max per spot.
- Chance % calibration: start with rating bands (go 70–95, marginal 35–70, nogo 0–35), refine with
  feedback.
- Station IDs: area file calls KSVR "Spanish Fork"; KSVR is South Valley Regional (West Jordan).
  FPS / Spanish Fork mapping needs verifying.
- Cherry upper launch coordinates/elevation TBD.
