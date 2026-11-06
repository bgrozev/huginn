# Speedflying — assessment knowledge

What the weather means for a speedflyer. The mechanisms (rotor, katabatic flow, outflow, mixing
down, …) are in [weather.md](weather.md); report conventions in [reporting.md](reporting.md).
Spot files (`spots/`) are the source of truth for site geometry, limits and local effects — when
they conflict with this file, the spot file wins.

## What matters for speedflying

- **Calm/light wind is ideal, not a problem.** There is no minimum wind threshold. Only flag wind
  that is too strong or from the wrong direction.
- **Once airborne, a speedflyer is committed to landing.** Abort decisions happen *before launch*.
  A wind increase before launch → do not launch.
- **Forward penetration is high.** Blow-back, benching-up and venturi drift are paragliding
  problems; they are low relevance for speedflying. Spot files tag such hazards `(PG only)` or
  `(low relevance for speedflying)` — omit those from speedflying reports.
- **Flights are low and close to terrain.** Low-level turbulence matters more than conditions at
  altitude; there is no climbing out of trouble.

## Hazards

None of these is "the main one" — check every slot against all of them.

| Hazard | Rating consequence |
|---|---|
| Rotor | Winds aloft match a spot's `rotor_triggers` → no-go (or as the spot file says). |
| Katabatic flow | Tail or cross on launch near sunset / dawn → marginal or no-go; say when it is expected to start. |
| Gust fronts / outflow | Storms in the region with outflow possible → at best marginal, usually no-go for affected slots. |
| Precipitation or storms nearby | Convective risk (LI < 0, CAPE, SPC outlook) in the region → at best marginal, usually no-go. |
| Virga | Visible virga in the local area → **no-go**. Always list as an on-site check when there is mid-level moisture or convection. |
| Thermal turbulence near terrain | Midday thermal transition is a reason to fly early or late, not a bonus → rate thermic slots marginal unless winds are very light. |

## Wind speed bands

Compare the **strongest wind expected at launch in the slot** — the higher of the top sustained speed
and the top gust — with these bands. Spots may override them with
`limits.speedflying.speed_bands_kt`.

| Band | Wind at launch | Meaning |
|---|---|---|
| Green | ≤ 10 kt | Ideal |
| Yellow | ≤ 15 kt | OK |
| Orange | ≤ 20 kt | Marginal |
| Red | > 20 kt | No-go |

Calm is green: there is no minimum.

## Wind direction vs. launch

- When a spot has `wind_rose_deg`, place the forecast direction in its bands: green = ideal (pass),
  yellow = OK (pass, note it), orange = marginal (warn), red = at the limit (fail, no-go). Outside
  every band = not flyable.
- Otherwise compare with the spot's `flyable_arc_deg`: on-face, cross, or tail. Outside the arc → at
  best marginal; check the spot for direction-specific rotor hazards (e.g. east-wind rotors at POM
  South) before rating.
- **Lee side.** Wind from behind the launch (roughly opposite its face) puts the launch in the lee of
  its own ridge — that *is* a rotor hazard. The rotor check then fails with "Lee side: wind from
  behind the ridge puts the launch in rotor". The direction check stays factual ("tail wind,
  350°"). Never mark the rotor check "not relevant".

## Gradient, mixing and timing

- Light gradient → the area's diurnal pattern decides which launch works when; use the area file.
- Strong gradient → don't count on the usual switch; rate by the gradient.
- Strong wind above light surface wind → the calm window ends when mixing starts. Give the expected
  time as a warning; plan the slot window to end before it.

## Pressure pattern

| Situation | For speedflying |
|---|---|
| High / ridge | Favorable, especially morning windows |
| Low / trough | Unfavorable — gusty, stronger gradient, convection |
| Falling pressure | Deteriorating — later slots worse |
| Rising pressure | Improving, but expect gusty post-frontal flow first |

## Precipitation

Wet wing, poor visibility, slick launch → no-go while it rains; marginal right after.
