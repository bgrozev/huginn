# Huginn

Speedflying conditions reports for predefined spots — 3 days × AM/PM, with the reasoning, warnings
and source links behind every call. Published at **https://huginn.mustelinae.net**.

> Experimental. Can be wrong. You alone decide whether to fly.

- [PLAN.md](PLAN.md) — architecture and roadmap
- [TODO.md](TODO.md) — feature backlog
- [knowledge/](knowledge/) — [weather](knowledge/weather.md) (general), [speedflying](knowledge/speedflying.md) (activity), [reporting](knowledge/reporting.md) (conventions).
  More specific wins: spot file > area `_group.md` > activity > weather.
- [spots/](spots/) — groups and spots (YAML front matter + local knowledge)
- [schema/report.schema.json](schema/report.schema.json) — report contract
- [site/](site/) — static site (renders `site/reports/*.json`)

## How a report is made

[.github/workflows/report.yml](.github/workflows/report.yml) runs daily at 12:00 UTC (05:00 MST /
06:00 MDT) and on demand (Actions → Daily report → Run workflow):

1. `scripts/fetch.py` downloads forecasts and observations → `raw/<run-id>.json` (kept 90 days as a
   run artifact, not committed).
2. Claude follows [agent/prompt.md](agent/prompt.md) → `site/reports/<run-id>.json`.
3. `scripts/validate.py` checks schema, coverage, chance bands and that every link was fetched.
4. `scripts/publish.py` updates `latest.json` and the history index; the run commits and deploys.

A failed run opens an issue. Auth: `CLAUDE_CODE_OAUTH_TOKEN` repo secret (from `claude setup-token`).

Run steps 1, 3, 4 locally with `pip install -r requirements.txt`; step 2 with
`claude -p "Follow agent/prompt.md exactly. RUN_ID=<id> RAW=raw/<id>.json trigger=manual"`.

## Local preview

```bash
python3 -m http.server 8765 --directory site
```

Open http://localhost:8765. `?r=<run-id>` opens an archived report; `#<spot>/<slot>` opens a cell.
