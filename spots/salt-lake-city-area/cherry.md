---
id: cherry
name: Cherry
group: salt-lake-city-area
activities: [speedflying]
launch: { lat: 40.5153, lon: -111.8270, elevation_ft: 7200, approximate: true, note: "Lower launch. Upper launch TBD." }
landing: { lat: 40.5181, lon: -111.8358, elevation_ft: 5400, approximate: true }
faces: NNW
flyable_arc_deg: [320, 20]
limits:
  # From v1 notes: "Very low winds required. Does not tolerate the speeds POM handles."
  # TODO: a number. Until set, anything beyond light winds is marginal at best.
  speedflying: { max_kt: null, note: "Very low winds only" }
best_time: calm
best_time_note: When gradient is light and conditions are calm.
rotor_triggers:
  - { when: "S/SSW flow aloft (700 mb / ~9,000 ft) at any meaningful speed", effect: "Site sits in rotor behind the ridge — NO-GO" }
links: []
---

# Cherry — local knowledge

Higher, NNW-facing launch east of POM. Needs calm conditions; much less wind tolerance than POM.

Coordinates and elevations are estimates — verify. This is the **lower launch**; the upper launch
is TBD.

## Hazards

- **Rotor from south winds aloft** — strong southerly flow at altitude is a strong indicator the site
  sits in rotor behind the ridge. Treat as **NO-GO** if winds aloft are S/SSW with any significant
  speed.
- **Higher elevation** — conditions change faster and are less predictable than at POM.
- **Longer approach to the LZ** — plan the escape route before launch.

## Field warnings

- **Rotor abort:** winds aloft (700 mb / ~9,000 ft) from the south at any meaningful speed → NO-GO.
  Site likely in rotor.
- **Abort trigger:** any sign of turbulence or irregular lift/sink on approach → do not launch.
