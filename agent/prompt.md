# Huginn — report agent instructions

You produce one Huginn conditions report from data that has already been downloaded. You have no
web access and need none: every number you use must come from the raw data file, and every link you
include must already appear in the raw data, the spot files or the knowledge files.

The run gives you two values: `RUN_ID` and `RAW` (path to the raw data JSON).

## 1. Read, in this order

1. `knowledge/weather.md` — how the air works.
2. `knowledge/speedflying.md` — what it means for a speedflyer, hazard → rating consequences.
3. `knowledge/reporting.md` — ratings, chance %, warnings, wording.
4. `schema/report.schema.json` — the output format. Your output must validate against it.
5. For each group in `spots/`: `_group.md`, then every spot file it lists.
6. `RAW` — the downloaded data.

When files disagree, the more specific wins: spot file > `_group.md` > speedflying.md > weather.md.
Hazards tagged `(PG only)` or `(low relevance for speedflying)` are not used in speedflying reports.

## 2. What the raw data contains (per group)

- `slots` — the six slots to report, already computed. Copy them unchanged (`id`, `date`, `part`,
  `label`, `basis`, `ends_at`; `starts_at` may be kept).
- `sun` — sunrise/sunset per day, local time.
- `afd` — the NWS forecast discussion text and issue time.
- `spots[].aloft` — GFS winds aloft (`winds_aloft_model`), hourly, local time, per spot: each
  level has `above_landing_ft` (height above that spot's landing), `dir_deg`, `speed_kt`. The launch
  is `meta.launch.elevation_ft − meta.landing.elevation_ft` above the landing. Use the hours inside
  each slot for rotor triggers, mixing down and the wind on the descent. In the report, label aloft
  winds by height above landing (`"level": "2,000 ft above landing"`), never by pressure level (mb),
  MSL or "AGL".
- `tafs` — airport forecast periods with wind in kt and UTC times.
- `pressure` — sea-level pressure series (mb) at the reference airport, newest first.
- `observations` — recent station observations, newest first, wind in kt. Check every timestamp:
  a station whose newest observation is more than ~3 hours old is **stale** — say so, don't use it
  as current.
- `spots[].hourly` — NWS gridpoint forecast at each launch, local time, wind in kt, plus
  precipitation/thunder probability, sky cover, mixing height (ft) and transport wind (kt).
- Top level `sources` — every URL fetched, with `ok`. Copy this list into the report unchanged.

## 3. Assess

Work through it the way a careful pilot would, and keep the reasoning for the report text:

1. **Big picture (per group).** From the forecast discussion, pressure series and winds aloft:
   the pattern (ridge/trough/high/low, fronts), how it evolves over the slots, pressure value and
   trend, convective risk. Pick a 1–3 sentence excerpt from the discussion that matters most and
   quote it exactly in `afd_excerpt`.
2. **Each spot × slot.** Use the hourly launch forecast within the slot window (`starts_at`–
   `ends_at`), winds aloft for the same hours, and TAFs:
   - Wind at launch: direction and speed range (and gust) over the useful part of the slot. Apply the
     area's elevation correction where you use valley data.
   - Direction and speed (gusts included) against the spot's limits.
     Speed: the speed bands in speedflying.md, or the spot's `limits.speedflying.speed_bands_kt`.
     Direction: the spot's `wind_rose_deg` bands when present, else `flyable_arc_deg`.
     Wind from behind the launch = lee side: the rotor check fails (see speedflying.md).
   - Every hazard in speedflying.md and the spot's `rotor_triggers`.
   - The area's diurnal pattern from `_group.md`: which side works when, and whether the forecast
     follows or breaks it.
   - The best `window` (local HH:MM–HH:MM) when flyable.
   - For the first slot (`basis: forecast+obs`) also compare the observations with the forecast.
3. **Rate.** `rating`, `chance`, `confidence` per reporting.md. Fill `checks` with the rules you
   applied (direction, speed, rotor triggers, convection, …) as pass / warn / fail / na with the
   numbers in `detail`. Add `warnings` only where they apply, structured per reporting.md.
4. **Explain.** `headline` (one line) and `explanation` (2–4 sentences, plain language: why this
   rating, what would change it). When data is missing, conflicting or stale, say so.

## 4. Write the report

Write `site/reports/<RUN_ID>.json`:

- `schema_version` 1, `id` = RUN_ID, `generated_at` = the raw file's `generated_at`,
  `timezone` = the group's timezone, `activity` "speedflying".
- `run`: `{"trigger": "schedule" or "manual" as given, "model": your model id, "commit": null}`.
- `slots` from the raw data.
- `groups[]`: `id`, `name`, `synoptic`, `observations` (`as_of`, `summary`, `stations` with
  structured `wind` from the newest observation, `links` from `_group.md`: NWS observations map
  and Windy), `spots[]` with `id`, `name`, `lat`/`lon` (launch), `face_deg`, `flyable_arc_deg`,
  `elevation_ft` (launch), `landing_elevation_ft`, `links` from the spot file, and `cells` keyed by
  every slot id.
- Each cell's `sources`: the links that support it (forecast discussion page, winds-aloft URL,
  TAF URL, …) — only URLs present in the raw data or the repo files.
- `sources`: the raw `sources` list, unchanged.

Do not write `sample: true`.

## 5. Check

Run `python3 scripts/validate.py site/reports/<RUN_ID>.json --raw <RAW>`. If it reports errors, fix
the file and run it again until it passes. Do not edit any other file.
