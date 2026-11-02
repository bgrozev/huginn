# Huginn

Speedflying conditions reports for predefined spots — 3 days × AM/PM, with the reasoning, warnings
and source links behind every call. Published at **https://huginn.mustelinae.net**.

> Experimental. Can be wrong. You alone decide whether to fly.

- [PLAN.md](PLAN.md) — architecture and roadmap
- [knowledge/speedflying.md](knowledge/speedflying.md) — activity knowledge
- [spots/](spots/) — groups and spots (YAML front matter + local knowledge)
- [schema/report.schema.json](schema/report.schema.json) — report contract
- [site/](site/) — static site (renders `site/reports/*.json`)

## Local preview

```bash
python3 -m http.server 8765 --directory site
```

Open http://localhost:8765. `?r=<run-id>` opens an archived report; `#<spot>/<slot>` opens a cell.
