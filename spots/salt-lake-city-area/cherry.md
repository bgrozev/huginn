---
id: cherry
name: Cherry
group: salt-lake-city-area
activities: [speedflying]
# Elevations from USGS NED 10 m terrain data.
launch: { lat: 40.5153, lon: -111.8270, elevation_ft: 6067, note: "Lower launch. Upper launch TBD." }
landing: { lat: 40.517985, lon: -111.835537, elevation_ft: 4855 }
faces: NNW
# Flyable = green..orange (red is the limit). Bands estimated from NED 10 m terrain (spur facing
# ~305°, rising ground from 045°) by analogy with POM North; narrower for low wind tolerance.
# Confidence low — terrain at these coordinates faces ~305°, not NNW (see launch note).
flyable_arc_deg: [290, 10]
wind_rose_deg:
  green: [[315, 345]]
  yellow: [[300, 315], [345, 0]]
  orange: [[290, 300], [0, 10]]
  red: [[280, 290], [10, 20]]
limits:
  # Very low winds only: overrides the general speedflying bands.
  speedflying: { speed_bands_kt: { green: 5, yellow: 10, orange: 15 } }
best_time: calm
best_time_note: When gradient is light and conditions are calm.
rotor_triggers:
  - { when: "S/SSW flow aloft (~2,000–4,000 ft above landing) at any meaningful speed", effect: "Site sits in rotor behind the ridge — NO-GO" }
links: []
---

# Cherry — local knowledge

Higher launch east of POM, on a spur running west-north-west (terrain at the launch faces ~305°).
Needs calm conditions; much less wind tolerance than POM.

This is the **lower launch** (~1,200 ft above the landing); the upper launch is TBD.

## Hazards

- **Rotor from south winds aloft** — strong southerly flow at altitude is a strong indicator the site
  sits in rotor behind the ridge. Treat as **NO-GO** if winds aloft are S/SSW with any significant
  speed.
- **Higher elevation** — conditions change faster and are less predictable than at POM.
- **Longer approach to the LZ** — plan the escape route before launch.

## Field warnings

- **Rotor abort:** winds aloft (~2,000–4,000 ft above landing) from the south at any meaningful speed → NO-GO.
  Site likely in rotor.
- **Abort trigger:** any sign of turbulence or irregular lift/sink on approach → do not launch.
