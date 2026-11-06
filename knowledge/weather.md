# Weather — general knowledge for free flight

How the air works and where to read it. Not tied to an activity or an area: activity files
(`speedflying.md`, later `paragliding.md`) say what each effect means for that discipline; area and
spot files (`spots/`) give the local pattern, altitudes and timing.

## Gradient vs. local (diurnal) wind

- **Gradient wind** is driven by the large-scale pressure pattern. **Diurnal (thermal) wind** is
  driven by the day's heating and the night's cooling of local terrain — valley, slope and lake/sea
  breezes, and drainage.
- **Light gradient** (ridge / high pressure) → the local diurnal cycle dominates and repeats
  predictably day to day.
- **Strong gradient** → the diurnal cycle is suppressed or delayed; an expected switch may never
  happen.
- **Mixing down.** At night and early morning the air near the ground is decoupled from the flow
  above. As the day heats up, the boundary layer deepens and the stronger wind above mixes down to
  the surface — often abruptly. Light surface wind under strong wind a few thousand feet up means
  the calm lasts only until mixing starts. Area files give the levels and typical timing.
- Every area has a normal diurnal pattern (documented in its area file). Flag any forecast that
  departs from it — pilots plan around it.

## Katabatic (downslope) flow

Air cooled against a slope gets denser and drains downhill. Mostly late afternoon through early
morning; strongest on clear, calm nights. It can start suddenly near sunset, accelerates in gullies
and canyons, and pools in valleys (the morning "drainage" flow in many valleys is katabatic air
moving down-valley).

## Rotor

Strong flow over a ridge or hill descends on the lee side and breaks into turbulent, tumbling eddies
at and below ridge height, sometimes far downwind. Surface wind in the lee can look light or even
reversed. The trigger is the wind *at and just above ridge height* from the direction that puts the
site in the lee — read winds aloft, not just the surface forecast.

## Convection, outflow and microbursts

- **Instability:** Lifted Index (LI) below 0 and CAPE above ~100 J/kg → showers and thunderstorms
  possible, usually afternoon. SPC outlooks give the regional risk.
- **Gust fronts / outflow:** a storm's downdraft spreads along the ground as a sharp wind shift and
  gust, often 20–40+ kt, and can run tens of miles ahead of the storm — storms out of sight still
  matter.
- **Microbursts:** small, violent downdrafts (under a mile across) with a burst of wind in all
  directions at the surface. Can come from modest-looking showers.
- **Virga:** precipitation evaporating before reaching the ground. Evaporation chills the air and
  accelerates it downward — a classic microburst source. Forecasts can't show virga; it is an
  on-site observation. Mid-level moisture plus a dry layer below is the setup.
- Precipitation itself: wet wing, poor visibility, slick launches.

## Thermals and turbulence

Surface heating builds thermals from mid-morning; the transition from smooth morning air to thermic
air is often rough. Thermals near terrain mean irregular lift, sink and gusts at low level.

## Inversions and stability

- Surface inversions trap calm, cold air in the morning; note when they are forecast to break.
- Mixing height / boundary-layer height tells how deep the mixed layer is — and so when and how
  strongly the wind above reaches the surface.

## Pressure pattern

Identify whether the area is under high, low, ridge or trough, and the trend.

| Situation | Typical weather |
|---|---|
| High / ridge | Stable, light gradient, local cycle dominates |
| Low / trough | Unstable, gusty, stronger gradient, showers more likely |
| Falling pressure | Deteriorating, system approaching |
| Rising pressure | Improving, often gusty right after a front |

Sea-level pressure: from the latest METAR at a nearby airport (altimeter inHg × 33.86 ≈ mb, or SLP
directly).

## Fronts

Frontal passages bring wind shifts, gusts and precipitation. Post-frontal flow is usually strong and
gusty for a day or so; its direction depends on the region (see area files). Give the front's ETA.

## Observations

- Observations exist only for now. Use them for the nearest slot; later slots are forecast-only.
- Compare observations to the forecast; where they diverge, trust the forecast less for the nearest
  slot.
- Stations rarely sit at launch height. Area files give the correction from valley stations to
  launch.
- Station timestamps matter: evening observations say little about the next morning.

## Units

- Work in **knots**. km/h → kt: ÷ 1.852. mph → kt: ÷ 1.151.
- Winds-aloft text forecast (FD) is already in kt. Format `DDSS`: DD = direction ×10°, SS = speed.
  `2714` → 270°/14 kt. `9900` → light and variable. `7799` → missing.

## Data sources

| Source | Use | URL |
|---|---|---|
| NWS Area Forecast Discussion | Synoptic pattern, forecaster reasoning, confidence | `https://api.weather.gov/products?type=AFD&location={wfo}` |
| NWS gridpoint forecast | Hourly wind at launch coordinates | `https://api.weather.gov/points/{lat},{lon}` → `forecastGridData` |
| Winds aloft (FD) | Gradient & rotor triggers by level | `https://aviationweather.gov/api/data/windtemp?region={region}&level=low&fcst=06\|12\|24` |
| TAF | Hourly-ish wind incl. gusts at nearby airports | `https://aviationweather.gov/api/data/taf?ids={ids}&format=json` |
| Station observations | Current wind for nearest slot | `https://api.weather.gov/stations/{id}/observations?limit=5` |
| GFA | Graphical forecast, link only | `https://aviationweather.gov/gfa/` |
| Prog chart (fronts & pressure) | Fronts/pressure, link only | `https://aviationweather.gov/gfa/#progchart` (old `/progchart/sfc` returns 403) |
| SPC outlook / mesoanalysis | Convective risk, link only | `https://www.spc.noaa.gov/products/outlook/` |
| NWS observations map | Live station winds, link only | `https://www.weather.gov/wrh/hazards?obs=true&wfo={wfo}&center={lat},{lon}&zoom=11` (needs `wfo` or obs don't load) |
| Windy | Model wind map, link only | `https://www.windy.com/?{lat},{lon},11` |

Winds-aloft region codes: `slc` Intermountain West, `sfo` West Coast, `dfw` South Central,
`chi` Midwest.

NWS station timeseries pages (`weather.gov/wrh/timeseries?site=…`) are JavaScript-rendered — use
them as chart links, fetch values from the API instead.
