"""Generate the sample report in site/reports/ (hand-written scenario, not real data).

Usage: python3 scripts/make_sample.py site/reports
"""
import json, sys, os

out = sys.argv[1]
AFD = "https://forecast.weather.gov/product.php?site=SLC&issuedby=SLC&product=AFD"
FD = "https://aviationweather.gov/api/data/windtemp?region=slc&level=low&fcst=12"
TAF = "https://aviationweather.gov/api/data/taf?ids=KSLC,KPVU&format=raw"

slots = [
    {"id": "d1-am", "date": "2026-11-02", "part": "am", "label": "Mon AM", "basis": "forecast+obs", "ends_at": "2026-11-02T19:00:00Z"},
    {"id": "d1-pm", "date": "2026-11-02", "part": "pm", "label": "Mon PM", "basis": "forecast", "ends_at": "2026-11-03T01:00:00Z"},
    {"id": "d2-am", "date": "2026-11-03", "part": "am", "label": "Tue AM", "basis": "forecast", "ends_at": "2026-11-03T19:00:00Z"},
    {"id": "d2-pm", "date": "2026-11-03", "part": "pm", "label": "Tue PM", "basis": "forecast", "ends_at": "2026-11-04T01:00:00Z"},
    {"id": "d3-am", "date": "2026-11-04", "part": "am", "label": "Wed AM", "basis": "forecast", "ends_at": "2026-11-04T19:00:00Z"},
    {"id": "d3-pm", "date": "2026-11-04", "part": "pm", "label": "Wed PM", "basis": "forecast", "ends_at": "2026-11-05T01:00:00Z"},
]

aloft = {
    "d1-am": [(320, 22), (320, 28)], "d1-pm": [(320, 18), (330, 24)],
    "d2-am": [(290, 8), (280, 12)], "d2-pm": [(310, 9), (290, 12)],
    "d3-am": [(200, 9), (210, 14)], "d3-pm": [(200, 14), (210, 19)],
}

def wind(slot, launch_dir, launch_kt, gust=None):
    a = aloft[slot]
    return {
        "launch": {"dir_deg": launch_dir, "speed_kt": launch_kt, **({"gust_kt": gust} if gust else {})},
        "aloft": [
            {"level": "6,000 ft", "dir_deg": a[0][0], "speed_kt": a[0][1]},
            {"level": "9,000 ft (700 mb)", "dir_deg": a[1][0], "speed_kt": a[1][1]},
        ],
    }

def cell(rating, chance, conf, headline, w, checks, explanation, window=None, warnings=()):
    c = {"rating": rating, "chance": chance, "confidence": conf, "headline": headline,
         "wind": w, "checks": [dict(zip(("rule", "result", "detail"), k)) for k in checks],
         "warnings": list(warnings), "explanation": explanation,
         "sources": [{"label": "NWS forecast discussion (Salt Lake City)", "url": AFD}, {"label": "Winds aloft forecast (12 h)", "url": FD}, {"label": "Airport forecasts — Salt Lake & Provo (TAF)", "url": TAF}]}
    if window: c["window"] = window
    return c

ROTOR_STEEP = {"severity": "abort", "title": "NW flow aloft — Steep Mountain rotor",
    "why": "Strong NW flow over Steep Mountain leaves a lee rotor at launch height on the north side.",
    "triggered_by": "Winds aloft 9,000 ft 320°/28 kt (12 h forecast)",
    "investigate": "Brisk + buoyant feel at the top or the sock cycling calm→strong = rotor. Do not launch."}
THERMAL = {"severity": "caution", "title": "Midday thermal transition",
    "why": "Thermals near terrain make a speedflying line rough and unpredictable; the diurnal switch passes through POM around midday.",
    "triggered_by": "Clear skies, ridge, mixing height ~9,000 ft by 13:00",
    "investigate": "Watch the valley stations for the S→N switch; fly before thermals start or after the switch settles."}
SOUTH_ROTOR = lambda kt: {"severity": "abort" if kt >= 15 else "caution", "title": "South flow aloft — Cherry rotor",
    "why": "Southerly flow over the ridge puts Cherry's NNW face in the lee — rotor at launch.",
    "triggered_by": f"Winds aloft 9,000 ft 210°/{kt} kt (winds aloft forecast)",
    "investigate": "Any irregular lift/sink or gusts from behind on approach → do not launch."}
INCREASE = {"severity": "abort", "title": "Possible high wind",
    "triggered_by": "S gradient could mix down after sunrise",
    "investigate": "If wind at launch builds while you set up, don't launch."}

S, N, C = "pom-south", "pom-north", "cherry"
cells = {S: {}, N: {}, C: {}}

cells[S]["d1-am"] = cell("marginal", 40, "medium", "Light S drainage under NW flow aloft",
    wind("d1-am", 170, [4, 9]),
    [("Direction in 160°–200°", "pass", "Est. 170° at launch: Point of the Mountain station S 3 kt, +3–8 kt for launch height"),
     ("Speed ≤ 22 kt incl. gusts", "pass", "4–9 kt"),
     ("No rotor trigger aloft", "warn", "NW 22–28 kt aloft — not a listed POM South trigger, but gradient opposes the drainage"),
     ("Obs agree with forecast", "warn", "Point of the Mountain S 3 kt, Salt Lake airport NW 8 kt — transition zone near POM")],
    "Post-frontal NW flow aloft fights the morning south drainage. The drainage is there but weak "
    "(Point of the Mountain station S 3 kt at 05:00), and Salt Lake airport already shows NW — the switch could come early. Short, "
    "uncertain window right after sunrise.", window="07:15–08:30", warnings=[INCREASE])
cells[S]["d1-pm"] = cell("nogo", 5, "high", "N flow — tail wind on a south face", wind("d1-pm", 330, [8, 14], 18),
    [("Direction in 160°–200°", "fail", "330° forecast at launch")], "Afternoon N flow puts POM South in the lee.")
cells[S]["d2-am"] = cell("go", 85, "medium", "Ridge, clean S drainage", wind("d2-am", 175, [6, 11]),
    [("Direction in 160°–200°", "pass", "175°"), ("Speed ≤ 22 kt incl. gusts", "pass", "6–11 kt"),
     ("No rotor trigger aloft", "pass", "WNW 8–12 kt aloft, light")],
    "Ridge builds overnight, gradient light. Classic morning: S drainage on the face until the switch "
    "around 11:00.", window="07:30–10:30", warnings=[THERMAL, INCREASE])
cells[S]["d2-pm"] = cell("nogo", 10, "medium", "Diurnal switch to N", wind("d2-pm", 340, [6, 10]),
    [("Direction in 160°–200°", "fail", "340°")], "After the switch POM South is in the lee.")
cells[S]["d3-am"] = cell("go", 75, "medium", "S drainage + light S gradient", wind("d3-am", 180, [8, 14], 16),
    [("Direction in 160°–200°", "pass", "180°"), ("Speed ≤ 22 kt incl. gusts", "pass", "8–14 G16 kt"),
     ("No rotor trigger aloft", "pass", "SSW 9–14 kt aloft")],
    "Ridge shifts east, flow aloft turns SSW. Drainage plus gradient — stronger and steadier than Tuesday, "
    "and the switch may be late.", window="07:30–11:00", warnings=[INCREASE])
cells[S]["d3-pm"] = cell("marginal", 35, "low", "S gradient may hold — gusty", wind("d3-pm", 190, [12, 18], 24),
    [("Direction in 160°–200°", "pass", "190°"), ("Speed ≤ 22 kt incl. gusts", "fail", "Gusts to 24 kt possible")],
    "If the S gradient overrides the diurnal switch, POM South stays on but gusts approach the max.", warnings=[THERMAL])

cells[N]["d1-am"] = cell("nogo", 15, "medium", "Drainage S + NW rotor aloft", wind("d1-am", 190, [3, 8]),
    [("Direction in 270°–360°", "fail", "S drainage at launch"), ("No rotor trigger aloft", "fail", "NW 28 kt at 9,000 ft")],
    "Morning drainage is a tail wind here, and the NW flow aloft is the Steep Mountain rotor trigger.", warnings=[ROTOR_STEEP])
cells[N]["d1-pm"] = cell("nogo", 20, "medium", "On-face, but NW rotor trigger aloft", wind("d1-pm", 330, [10, 16], 20),
    [("Direction in 270°–360°", "pass", "330°"), ("Speed ≤ max", "na", "No speedflying max set for POM North"),
     ("No rotor trigger aloft", "fail", "NW 24 kt at 9,000 ft")],
    "Surface direction is perfect, but this is exactly the setup that rotors off Steep Mountain.", warnings=[ROTOR_STEEP])
cells[N]["d2-am"] = cell("nogo", 10, "medium", "S drainage — tail wind", wind("d2-am", 175, [6, 11]),
    [("Direction in 270°–360°", "fail", "175°")], "Morning belongs to the south side.")
cells[N]["d2-pm"] = cell("go", 80, "medium", "Clean N switch under a ridge", wind("d2-pm", 340, [8, 12]),
    [("Direction in 270°–360°", "pass", "340°"), ("Speed ≤ max", "na", "No speedflying max set; 8–12 kt is within P2/M1 range"),
     ("No rotor trigger aloft", "pass", "WNW 9–12 kt aloft — light")],
    "Light gradient lets the diurnal switch complete. Smoothest about 2 h before sunset (~15:00–17:00).",
    window="15:00–17:00")
cells[N]["d3-am"] = cell("nogo", 5, "medium", "S drainage + S gradient", wind("d3-am", 180, [8, 14]),
    [("Direction in 270°–360°", "fail", "180°")], "Tail wind.")
cells[N]["d3-pm"] = cell("marginal", 35, "low", "Switch may not happen", wind("d3-pm", 350, [4, 9]),
    [("Direction in 270°–360°", "warn", "N if the switch happens; S gradient may hold"),
     ("No rotor trigger aloft", "pass", "SSW aloft, not a POM North trigger")],
    "SSW gradient aloft could suppress the afternoon switch. At 14:00 compare Salt Lake airport with the south valley stations.")

cells[C]["d1-am"] = cell("marginal", 40, "low", "On-face NW, but 22–28 kt aloft", wind("d1-am", 320, [6, 12]),
    [("Direction in 320°–020°", "pass", "320°"), ("Very light wind only", "warn", "6–12 kt est. — more than Cherry likes"),
     ("No S flow aloft", "pass", "NW aloft")],
    "Direction suits the face and there's no south rotor risk, but post-frontal NW flow is stronger than Cherry tolerates.")
cells[C]["d1-pm"] = cell("nogo", 15, "medium", "Thermal + NW gradient", wind("d1-pm", 320, [10, 16], 20),
    [("Very light wind only", "fail", "10–16 G20 kt")], "Too much wind for Cherry.", warnings=[THERMAL])
cells[C]["d2-am"] = cell("go", 70, "medium", "Calm ridge morning", wind("d2-am", 340, [0, 5]),
    [("Direction in 320°–020°", "pass", "Light, ~340°"), ("Very light wind only", "pass", "0–5 kt"),
     ("No S flow aloft", "pass", "WNW 8–12 kt")],
    "Best Cherry setup of the period: light gradient, no south flow aloft.", window="08:00–10:30")
cells[C]["d2-pm"] = cell("marginal", 45, "medium", "Light but thermic", wind("d2-pm", 330, [5, 10]),
    [("Very light wind only", "warn", "5–10 kt, thermic")], "Flyable direction; thermals near terrain are the concern.", warnings=[THERMAL])
cells[C]["d3-am"] = cell("marginal", 35, "medium", "S flow aloft starting", wind("d3-am", 0, [2, 6]),
    [("No S flow aloft", "warn", "SSW 14 kt at 9,000 ft")], "Surface is calm, but south flow aloft is the rotor trigger.",
    warnings=[SOUTH_ROTOR(14)])
cells[C]["d3-pm"] = cell("nogo", 10, "medium", "S flow aloft — rotor", wind("d3-pm", 200, [4, 10]),
    [("No S flow aloft", "fail", "SSW 19 kt at 9,000 ft")], "Classic Cherry rotor setup.", warnings=[SOUTH_ROTOR(19)])

spots = [
    {"id": S, "name": "POM South", "lat": 40.4567, "lon": -111.9027, "face": "S", "flyable_arc_deg": [160, 200], "elevation_ft": 5148,
     "links": [{"label": "UHGPGA site guide", "url": "https://www.uhgpga.org/pom-south-side"}], "cells": cells[S]},
    {"id": N, "name": "POM North", "lat": 40.4745, "lon": -111.8928, "face": "N", "flyable_arc_deg": [270, 360], "elevation_ft": 5100,
     "links": [{"label": "UHGPGA site guide", "url": "https://www.uhgpga.org/pom-north-side"}], "cells": cells[N]},
    {"id": C, "name": "Cherry", "lat": 40.5153, "lon": -111.8270, "face": "NNW", "flyable_arc_deg": [320, 20], "elevation_ft": 7200, "links": [], "cells": cells[C]},
]

report = {
    "schema_version": 1,
    "id": "sample",
    "sample": True,
    "generated_at": "2026-11-02T12:00:00Z",
    "timezone": "America/Denver",
    "activity": "speedflying",
    "run": {"trigger": "manual", "model": None, "commit": None},
    "slots": slots,
    "groups": [{
        "id": "salt-lake-city-area", "name": "Salt Lake City Area",
        "synoptic": {
            "summary": "Sunday's cold front has cleared east. Post-frontal NW flow aloft eases through Monday as a ridge "
                       "builds Tuesday — light gradient, classic diurnal cycle. Wednesday the ridge shifts east and flow aloft "
                       "turns SSW ahead of the next trough.",
            "pressure": {"system": "ridge", "value_mb": 1024, "trend": "rising",
                         "significance": "Rising pressure behind the front; ridge overhead Tuesday is the most favorable day."},
            "afd_excerpt": "SAMPLE — not a real AFD quote.",
            "links": [{"label": "NWS forecast discussion (Salt Lake City)", "url": AFD},
                      {"label": "Aviation forecast map (GFA)", "url": "https://aviationweather.gov/gfa/"},
                      {"label": "Fronts & pressure chart", "url": "https://aviationweather.gov/gfa/#progchart"},
                      {"label": "Thunderstorm outlook (SPC)", "url": "https://www.spc.noaa.gov/products/outlook/"}],
        },
        "observations": {
            "as_of": "2026-11-02T11:55:00Z",
            "summary": "Drainage S at Point of the Mountain, Salt Lake airport already NW — transition zone near POM. Add 3–8 kt for launch elevation.",
            "stations": [
                {"id": "E7701", "name": "Point of the Mountain", "url": "https://www.weather.gov/wrh/timeseries?site=E7701&hours=72", "wind": {"dir_deg": 170, "speed_kt": 3}, "summary": "drainage"},
                {"id": "KSLC", "name": "Salt Lake airport", "url": "https://www.weather.gov/wrh/timeseries?site=KSLC&hours=72", "wind": {"dir_deg": 320, "speed_kt": 8}},
                {"id": "FPS", "name": "Spanish Fork", "url": "https://www.weather.gov/wrh/timeseries?site=FPS&hours=72", "wind": {"dir_deg": 160, "speed_kt": 5}},
                {"id": "KPVU", "name": "Provo airport", "url": "https://www.weather.gov/wrh/timeseries?site=KPVU&hours=72", "wind": {"dir_deg": None, "speed_kt": 0}},
            ],
            "links": [{"label": "NWS observations map", "url": "https://www.weather.gov/wrh/hazards?obs=true&wfo=slc&center=40.48,-111.87&zoom=11"},
                      {"label": "Windy wind map", "url": "https://www.windy.com/?40.480,-111.870,11"}],
        },
        "spots": spots,
    }],
    "sources": [
        {"label": "NWS forecast discussion (Salt Lake City)", "url": AFD, "fetched_at": "2026-11-02T11:58:00Z", "ok": True},
        {"label": "Winds aloft forecast (12 h)", "url": FD, "fetched_at": "2026-11-02T11:58:00Z", "ok": True},
        {"label": "Airport forecasts — Salt Lake & Provo (TAF)", "url": TAF, "fetched_at": "2026-11-02T11:58:00Z", "ok": True},
        {"label": "Observations — Point of the Mountain (E7701)", "url": "https://api.weather.gov/stations/E7701/observations?limit=5", "fetched_at": "2026-11-02T11:59:00Z", "ok": True},
    ],
}

os.makedirs(out, exist_ok=True)
for name in ("sample.json", "latest.json"):
    with open(os.path.join(out, name), "w") as f:
        json.dump(report, f, indent=1, ensure_ascii=False)
with open(os.path.join(out, "index.json"), "w") as f:
    json.dump({"reports": [{"id": "sample", "generated_at": report["generated_at"], "summary": "Sample report"}]}, f, indent=1)
