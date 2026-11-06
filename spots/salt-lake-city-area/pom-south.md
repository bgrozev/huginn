---
id: pom-south
name: POM South
group: salt-lake-city-area
activities: [speedflying, paragliding]
launch: { lat: 40.4567, lon: -111.9027, elevation_ft: 5148 }
landing: { lat: 40.4567, lon: -111.9027, elevation_ft: 4834, approximate: true }
# Direction the launch faces (terrain aspect, USGS 10 m data).
face_deg: 150
# Flyable = green..orange (red is the limit). Bands estimated from NED 10 m terrain (aspect ~147°,
# ridge ~045/240°) by analogy with POM North's pilot wind rose, keeping the site guide's 160° cut-off
# for the rotor off the hills at ~120°–160°. Confidence medium — confirm how far past 200° is flyable.
flyable_arc_deg: [155, 215]
wind_rose_deg:
  green: [[170, 195]]
  yellow: [[160, 170], [195, 205]]
  orange: [[155, 160], [205, 215]]
  red: [[150, 155], [215, 225]]
limits:
  # speedflying: general speed bands from knowledge/speedflying.md
  # (v1 notes had "speed/mini wing ideal 14–17 kt, max 22 kt")
  paragliding: { max_kt: 13, note: "P2 max" }
best_time: am
best_time_note: First 2–3 h after sunrise, before the diurnal switch.
rotor_triggers:
  - { when: "surface or aloft flow below 160° (from ~90°–160°)", effect: "Rotors off the hills toward ~135° from launch" }
  - { when: "flow from ~270°", effect: "Bowl rotor at the west end" }
links:
  - { label: UHGPGA site guide, url: "https://www.uhgpga.org/pom-south-side" }
---

# POM South — local knowledge

South face of Point of the Mountain. Morning site: drainage flow from Utah Valley loads it until
the diurnal switch to flow from ~340°.

## Hazards

- **Rotor below 160°** — hills toward ~135° from launch. Reject while flow is below 160°; wait for
  160° or more.
- **Bowl rotor with flow from ~270°** — west-end bowl.
- **Midday thermal turbulence** — rapid transition. Speedflying in thermals near terrain is
  hazardous; morning window closes when thermals start.

## Field warnings

- **Abort trigger:** wind increase before launch → do not launch. (Once airborne, a speedflyer is
  committed to landing — this is not an in-flight abort.)

## Notes from past reports

- With a strong ~180° gradient (trough upstream), TAF gusts at KSLC (e.g. 180°/14 G22 kt) mean launch
  is past the 22 kt max once mixing starts (~10:00). The usable slot shrinks to early morning.
