# Reporting — conventions for every report

How to express an assessment, whatever the activity. Field definitions:
[schema/report.schema.json](../schema/report.schema.json).

## Ratings

| Rating | Meaning |
|---|---|
| `go` | Meets the spot's flyability criteria, no significant hazards |
| `marginal` | Borderline — speed near limits, timing uncertain, or one factor questionable |
| `nogo` | Clearly outside criteria, or a hazard is present |
| `unknown` | Insufficient data — say so, don't guess |

When borderline, explain the tension (e.g. "speed fits but direction is 20° cross — marginal").

## Chance of flyability

`chance` is the estimated chance the slot meets the spot's criteria — not model confidence.
Provisional bands until calibrated with feedback: go 70–95, marginal 35–70, nogo 0–35. Report data
quality separately as `confidence` (high/medium/low).

## Slots and observations

- Six slots, AM/PM over three days, starting at the next slot that isn't over yet.
- Only the nearest slot uses observations (`basis: forecast+obs`); later slots are forecast-only.
- Label observation times; don't present stale observations as current.

## Warnings

Each warning should teach, not just alarm — but stay short:

- **title** — short and plain, e.g. "South flow aloft — rotor risk", "Possible high wind"
- **why** — the mechanism (what the terrain/air does). Omit when obvious (e.g. high wind).
- **triggered_by** — the data that fired it (value + source)
- **investigate** — what the pilot should check on site (sock behaviour, valley station, virga, etc.)
- **severity** — `info`, `caution`, or `abort` (abort = do-not-launch trigger)

## Writing for the reader

- **All wind speeds in knots (kt).** Never m/s or km/h in output.
- Winds in structured fields are numbers (`dir_deg`, `speed_kt`, `gust_kt`); the site draws the
  arrow. Don't add compass letters next to degrees ("160°", not "SSE 160°"). Prose can still say
  "south drainage".
- Name stations and products in plain words; put codes in parentheses only where useful:
  "Point of the Mountain station", "Salt Lake airport (KSLC)" — not "E7701", "KSLC".
- Link labels say what the page is: "NWS forecast discussion (Salt Lake City)", "Winds aloft
  forecast (GFS)", "Airport forecasts — Salt Lake & Provo (TAF)", "Aviation forecast map (GFA)",
  "Fronts & pressure chart", "Thunderstorm outlook (SPC)" — not "AFD — SLC", "GFA".
- When data is missing or ambiguous, say so rather than guessing.
