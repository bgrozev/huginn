---
id: pom-north
name: POM North
group: salt-lake-city-area
activities: [speedflying, paragliding]
launch: { lat: 40.4745, lon: -111.8928, elevation_ft: 5100 }
landing: { elevation_ft: 4700, approximate: true }
# Direction the launch faces (terrain aspect, USGS 10 m data).
face_deg: 330
# Flyable = green..orange (red is the limit). Bands from the pilot's wind rose for this launch.
flyable_arc_deg: [280, 40]
wind_rose_deg:
  green: [[310, 10]]
  yellow: [[290, 310], [10, 30]]
  orange: [[280, 290], [30, 40]]
  red: [[260, 280], [40, 50]]
limits:
  # speedflying: general speed bands from knowledge/speedflying.md
  paragliding: { max_kt: 16, ideal_kt: [10, 14], gust_tolerance_kt: 4, note: "P2/M1" }
best_time: pm
best_time_note: Afternoon/evening after the diurnal switch to flow from ~340°; smoothest ~2 h before sunset.
rotor_triggers:
  - { when: "strong flow aloft from ~290°–340°", effect: "Lee rotor off Steep Mountain at launch height — do not launch" }
  - { when: "crosswind from ~60°–120°", effect: "Ground turbulence in the lee of the launch fingers" }
links:
  - { label: UHGPGA site guide, url: "https://www.uhgpga.org/pom-north-side" }
---

# POM North — local knowledge

North face of Point of the Mountain. Afternoon/evening site: loads after the diurnal switch to ~340°
flow.

## Hazards

- **Steep Mountain rotors** — lee rotors on the entire Steep Mountain face, relevant at launch height.
  Strong flow aloft from ~290°–340° = do not launch.
- **Crosswind from ~60°–120°** — ground turbulence in the lee of the launch fingers.
- **Wind gradient on descent** — brisk over the bench → calm near the ground. Normal for a
  speedflying descent; expect it.

## Field warnings

- **Rotor signal at launch:** brisk + buoyant feel at the top with flow aloft from ~290°–340° → do not launch (lee
  rotor from Steep Mountain).
- **Abort trigger:** windsock cycling calm → strong more than once in 5 min = mechanical turbulence.
  Do not launch.
