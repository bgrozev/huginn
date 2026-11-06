---
id: salt-lake-city-area
name: Salt Lake City Area
centroid: { lat: 40.490, lon: -111.868 }
timezone: America/Denver
wfo: SLC
taf_airports: [KSLC, KPVU]
pressure_reference: KSLC
spots: [pom-south, pom-north, cherry]
observation_stations:
  - { id: E7701, name: Point of the Mountain, url: "https://www.weather.gov/wrh/timeseries?site=E7701&hours=72" }
  - { id: FPS, name: Spanish Fork, url: "https://www.weather.gov/wrh/timeseries?site=FPS&hours=72" }
  - { id: UT7, name: Draper, url: "https://www.weather.gov/wrh/timeseries?site=UT7&hours=72" }
  - { id: UTALP, name: Alpine, url: "https://www.weather.gov/wrh/timeseries?site=UTALP&hours=72" }
  - { id: F3671, name: Lehi, url: "https://www.weather.gov/wrh/timeseries?site=F3671&hours=72" }
  - { id: KSVR, name: South Valley Regional, url: "https://www.weather.gov/wrh/timeseries?site=KSVR&hours=72" }
  - { id: KSLC, name: Salt Lake Intl, url: "https://www.weather.gov/wrh/timeseries?site=KSLC&hours=72" }
  - { id: KPVU, name: Provo, url: "https://www.weather.gov/wrh/timeseries?site=KPVU&hours=72" }
observations_map: "https://www.weather.gov/wrh/hazards?obs=true&wfo=slc&center=40.48,-111.87&zoom=11"
windy_url: "https://www.windy.com/?40.480,-111.870,11"
afd_url: "https://forecast.weather.gov/product.php?site=SLC&issuedby=SLC&product=AFD"
---

# Salt Lake City Area — shared local knowledge

Spots: [POM South](pom-south.md), [POM North](pom-north.md), [Cherry](cherry.md).
Point of the Mountain (POM) sits at the gap between Salt Lake Valley (north) and Utah Valley (south).

## Dominant diurnal pattern

Cold air drains south-to-north toward the Great Salt Lake each morning (drainage flow). Valley
heating reverses this to a north-to-south return flow in the afternoon/evening. The switchover
point moves geographically through the day.

- **Morning**: south wind → loads **POM South**.
- **Afternoon/evening**: north wind → loads **POM North**.
- **Timing of the switch** depends on gradient strength. Light gradient (ridge): switch earlier and
  more complete. Strong gradient: diurnal pattern suppressed or delayed.

**Flag if the forecast diverges from this pattern.** Pilots plan their day around this cycle.

## Mixing down here

The valley floor is ~4,500 ft. Watch winds aloft at **850 and 700 mb (~5,000 and ~10,000 ft)**: light valley wind under
**20+ kt** at those levels means the calm ends when the boundary layer deepens, typically **late
morning (~10:00)**. With a strong S gradient this is what closes the POM South morning slot.

## Fronts here

Post-frontal flow in the Intermountain West is usually strong, gusty **NW** for a day or so after a
cold front — directly the Steep Mountain rotor trigger for POM North.

## Reading the stations

- South-valley station reports south flow → POM South likely active.
- KSLC reports N/NW but the south-valley station still reports S → transition zone at or near POM.
- Both report the same direction → gradient has overridden the diurnal pattern.

**E7701** (Point of the Mountain) is the most direct launch-area reference when it reports.
**FPS** (Spanish Fork) is the best indicator for south valley flow / POM South conditions.

## Elevation correction

Stations sit near valley elevation (~4,200–4,800 ft). Launches are 5,100–7,200 ft.
**Add 3–8 kt to valley obs to estimate launch wind.** NWS timeseries pages show mph — convert to kt
(÷ 1.151).

## Seasonal / misc

- Times are America/Denver: MDT (UTC−6) in summer, MST (UTC−7) after DST ends.
