# Speedflying — assessment knowledge

Site-independent knowledge for assessing speedflying conditions. Extracted from the v1
`weather-flying` skill. Spot files (`spots/`) are the source of truth for site geometry, limits and
local effects — when they conflict with this file, the spot file wins.

## What matters for speedflying

- **Calm/light wind is ideal, not a problem.** There is no minimum wind threshold. Only flag wind
  that is too strong or from the wrong direction.
- **Once airborne, a speedflyer is committed to landing.** Abort decisions happen *before launch*.
  A wind increase before launch → do not launch.
- **Forward penetration is high.** Blow-back, benching-up and venturi drift are paragliding
  problems; they are low relevance for speedflying. Spot files tag such hazards `(PG only)` or
  `(low relevance for speedflying)` — omit those from speedflying reports.
- **Thermal turbulence near terrain is hazardous.** Speedflying hugs the terrain; midday thermal
  transitions are a reason to fly early or late, not a bonus.
- **Rotor is the dominant terrain hazard.** Strong flow aloft over a ridge upwind of launch puts the
  launch in rotor even if surface wind looks fine. Check winds aloft direction against each spot's
  rotor triggers.

## Ratings

| Rating | Meaning |
|---|---|
| `go` | Meets the spot's flyability criteria, no significant hazards |
| `marginal` | Borderline — speed near limits, timing uncertain, or one factor questionable |
| `nogo` | Clearly outside criteria, or a hazard is present |
| `unknown` | Insufficient data — say so, don't guess |

When borderline, explain the tension (e.g. "speed fits but direction is 20° cross — marginal").

## Wind direction vs. launch

- Compare forecast wind direction to the spot's flyable arc: on-face, cross, or tail.
- Direction outside the arc → at best marginal; check the spot for direction-specific rotor
  hazards (e.g. east-wind rotors at POM South) before rating.

## Gradient vs. diurnal (thermal) wind

- Light gradient (ridge / high) → local diurnal cycle dominates and is predictable.
- Strong gradient → diurnal pattern suppressed or delayed; switch may never happen.
- **Gradient mixing down**: once the boundary layer deepens (late morning), stronger winds aloft mix
  to the surface. Light valley wind under 20+ kt at 6–9k ft means the calm window ends when mixing
  starts. Note this as a shear/mixing warning with the expected time.
- Flag any forecast that diverges from the area's normal diurnal pattern — pilots plan around it.

## Pressure pattern

Identify whether the area is under high, low, ridge or trough, and the trend.

| Situation | Meaning for speedflying |
|---|---|
| High / ridge | Stable, light gradient — favorable, especially morning windows |
| Low / trough | Instability, gusty, stronger gradient — unfavorable |
| Falling pressure | Deteriorating, system approaching |
| Rising pressure | Improving, often post-frontal gusty first |

Sea-level pressure: from the latest METAR at a nearby airport (altimeter inHg × 33.86 ≈ mb, or SLP
directly).

## Stability & convection

- Lifted Index (LI) negative and CAPE > ~100 J/kg → afternoon showers/thunderstorms possible;
  outflow gusts make afternoon slots unsafe.
- Surface inversions trap calm air in the morning; note when they are forecast to break.
- Mixing height / boundary-layer height tells when aloft wind reaches the surface.
- Precipitation: wet wing, poor visibility — rate the slot accordingly.

## Fronts

Frontal passages bring wind shifts, gusts and precip. Post-frontal flow is usually strong and gusty
(NW in the Intermountain West). Give the front ETA in the warning.

## Observations (nearest slot only)

- Observations exist only for the current period. Later slots are forecast-only — say so.
- Compare obs to forecast; flag where they diverge. Divergence lowers confidence for the nearest
  slot more than any single forecast value.
- Valley stations sit below launch. Apply the area's **elevation correction** (e.g. add 3–8 kt to
  valley obs to estimate launch wind).
- Old obs (e.g. evening obs in a report for the next morning) must be labelled with their time.

## Units

- **All wind speeds in knots (kt).** Never m/s or km/h in output.
- km/h → kt: ÷ 1.852. mph → kt: ÷ 1.151.
- Winds aloft text forecast is already in kt. Format `DDSS`: DD = direction ×10°, SS = speed kt.
  `2714` → 270°/14 kt. `9900` → light and variable. `7799` → missing.

## Data sources (generic)

| Source | Use | URL |
|---|---|---|
| NWS Area Forecast Discussion | Synoptic pattern, forecaster reasoning, confidence | `https://api.weather.gov/products?type=AFD&location={wfo}` |
| NWS gridpoint forecast | Hourly wind at launch coordinates | `https://api.weather.gov/points/{lat},{lon}` → `forecastGridData` |
| Winds aloft (FD) | Gradient & rotor triggers by level | `https://aviationweather.gov/api/data/windtemp?region={region}&level=low&fcst=06\|12\|24` |
| TAF | Hourly-ish wind incl. gusts at nearby airports | `https://aviationweather.gov/api/data/taf?ids={ids}&format=json` |
| Station observations | Current wind for nearest slot | `https://api.weather.gov/stations/{id}/observations?limit=5` |
| GFA | Graphical forecast, link only | `https://www.aviationweather.gov/gfa` |
| Surface prog chart | Fronts/pressure, link only | `https://www.aviationweather.gov/progchart/sfc` |
| SPC outlook / mesoanalysis | Convective risk, link only | `https://www.spc.noaa.gov/products/outlook/` |

Winds-aloft region codes: `slc` Intermountain West, `sfo` West Coast, `dfw` South Central,
`chi` Midwest.

NWS station timeseries pages (`weather.gov/wrh/timeseries?site=…`) are JavaScript-rendered — use
them as chart links, fetch values from the API instead.

## Warnings — how to write them

Each warning should teach, not just alarm:

- **title** — short, e.g. "South flow aloft — rotor risk"
- **why** — the mechanism (what the terrain/air does)
- **triggered_by** — the data that fired it (value + source)
- **investigate** — what the pilot should check on site (sock behaviour, valley station, etc.)
- **severity** — `info`, `caution`, or `abort` (abort = do-not-launch trigger)

## Chance of flyability

`chance` is the estimated chance the slot meets the spot's criteria — not model confidence.
Provisional bands until calibrated with feedback: go 70–95, marginal 35–70, nogo 0–35. Report data
quality separately as `confidence` (high/medium/low).
