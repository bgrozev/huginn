---
id: pom-north
name: POM North
group: salt-lake-city-area
activities: [speedflying, paragliding]
launch: { lat: 40.4745, lon: -111.8928, elevation_ft: 5100 }
landing: { elevation_ft: 4700, approximate: true }
faces: N
flyable_arc_deg: [270, 360]
limits:
  speedflying: { max_kt: null }
  paragliding: { max_kt: 16, ideal_kt: [10, 14], gust_tolerance_kt: 4, note: "P2/M1" }
best_time: pm
best_time_note: Afternoon/evening after the diurnal switch to north; smoothest ~2 h before sunset.
rotor_triggers:
  - { when: "strong NW flow aloft", effect: "Lee rotor off Steep Mountain at launch height — do not launch" }
  - { when: "E crosswind", effect: "Ground turbulence in the lee of the launch fingers" }
links:
  - { label: UHGPGA site guide, url: "https://www.uhgpga.org/pom-north-side" }
---

# POM North — local knowledge

North face of Point of the Mountain. Afternoon/evening site: loads after the diurnal switch to north
flow.

## Hazards

- **Steep Mountain rotors** — lee rotors on the entire Steep Mountain face, relevant at launch height.
  Strong NW flow aloft = do not launch.
- **Easterly crosswind** — ground turbulence in the lee of the launch fingers.
- **Wind gradient on descent** — brisk over the bench → calm near the ground. Normal for a
  speedflying descent; expect it.

## Field warnings

- **Rotor signal at launch:** brisk + buoyant feel at the top with NW flow aloft → do not launch (lee
  rotor from Steep Mountain).
- **Abort trigger:** windsock cycling calm → strong more than once in 5 min = mechanical turbulence.
  Do not launch.
