---
id: pom-south
name: POM South
group: salt-lake-city-area
activities: [speedflying, paragliding]
launch: { lat: 40.4567, lon: -111.9027, elevation_ft: 5148 }
landing: { lat: 40.4567, lon: -111.9027, elevation_ft: 4834, approximate: true }
faces: S
flyable_arc_deg: [160, 200]
limits:
  speedflying: { max_kt: 22, ideal_kt: [0, 17] }
  paragliding: { max_kt: 13, note: "P2 max" }
best_time: am
best_time_note: First 2–3 h after sunrise, before the diurnal switch.
rotor_triggers:
  - { when: "surface or aloft flow E/SE (< 160°)", effect: "Rotors off hills SE of launch" }
  - { when: "flow W", effect: "Bowl rotor at the west end" }
links:
  - { label: UHGPGA site guide, url: "https://www.uhgpga.org/pom-south-side" }
---

# POM South — local knowledge

South face of Point of the Mountain. Morning site: drainage flow from Utah Valley loads it until
the diurnal switch to north.

## Hazards

- **East wind rotors** — hills southeast of launch. Reject while flow is SE (< 160°); wait for SSE.
- **West wind bowl rotor** — west-end bowl.
- **Midday thermal turbulence** — rapid transition. Speedflying in thermals near terrain is
  hazardous; morning window closes when thermals start.

## Field warnings

- **Abort trigger:** wind increase before launch → do not launch. (Once airborne, a speedflyer is
  committed to landing — this is not an in-flight abort.)

## Notes from past reports

- With a strong S gradient (trough upstream), TAF gusts at KSLC (e.g. 180°/14 G22 kt) mean launch
  is past the 22 kt max once mixing starts (~10:00). The usable slot shrinks to early morning.
