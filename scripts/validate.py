"""Validate a report before it is published.

Usage: python3 scripts/validate.py site/reports/<run-id>.json [--raw raw/<run-id>.json]

Checks the JSON schema plus things a schema can't: the report covers every group, spot and slot
from the raw data; chance % fits the rating; every URL in the report exists in the raw data or in
the repo's spot/knowledge files (no invented links). Exit 1 with a list of errors on failure.
"""
import argparse
import glob
import json
import os
import re
import sys

import jsonschema

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL_RE = re.compile(r"https?://[^\s\"'`<>|)\]]+")
# Must match knowledge/reporting.md.
CHANCE_BANDS = {"go": (70, 95), "marginal": (35, 70), "nogo": (0, 35)}


def known_urls(raw):
    texts = [json.dumps(raw)] if raw else []
    for pattern in ("spots/**/*.md", "knowledge/*.md"):
        for p in glob.glob(os.path.join(ROOT, pattern), recursive=True):
            with open(p) as f:
                texts.append(f.read())
    urls = set()
    for t in texts:
        urls.update(u.rstrip(".,;:") for u in URL_RE.findall(t.replace("\\/", "/")))
    return urls


def report_urls(node):
    if isinstance(node, dict):
        for k, v in node.items():
            if k in ("url", "chart_url") and isinstance(v, str):
                yield v
            else:
                yield from report_urls(v)
    elif isinstance(node, list):
        for v in node:
            yield from report_urls(v)


def validate(report, raw, report_path):
    errors = []
    with open(os.path.join(ROOT, "schema", "report.schema.json")) as f:
        schema = json.load(f)
    for e in jsonschema.Draft202012Validator(schema).iter_errors(report):
        errors.append(f"schema: {e.json_path}: {e.message}")
    if errors:
        return errors  # structure is wrong; the checks below would only add noise

    stem = os.path.splitext(os.path.basename(report_path))[0]
    if report["id"] != stem:
        errors.append(f"id {report['id']!r} does not match file name {stem!r}")
    if report.get("sample"):
        errors.append("report is marked sample: true")

    slot_ids = [s["id"] for s in report["slots"]]
    if raw:
        if report["id"] != raw["run_id"]:
            errors.append(f"id {report['id']!r} != raw run_id {raw['run_id']!r}")
        if report["generated_at"] != raw["generated_at"]:
            errors.append("generated_at differs from the raw data")
        raw_slots = [s["id"] for s in raw["groups"][0]["slots"]]
        if slot_ids != raw_slots:
            errors.append(f"slots {slot_ids} != raw slots {raw_slots}")
        rep_groups = {g["id"]: g for g in report["groups"]}
        for rg in raw["groups"]:
            g = rep_groups.get(rg["id"])
            if not g:
                errors.append(f"group {rg['id']} missing")
                continue
            rep_spots = {s["id"] for s in g["spots"]}
            for rs in rg["spots"]:
                if rs["id"] not in rep_spots:
                    errors.append(f"{rg['id']}: spot {rs['id']} missing")
        if sorted(s["url"] for s in report["sources"]) != sorted(s["url"] for s in raw["sources"]):
            errors.append("sources differ from the raw sources list (copy it unchanged)")

    for g in report["groups"]:
        for s in g["spots"]:
            for sid in slot_ids:
                c = s["cells"].get(sid)
                where = f"{g['id']}/{s['id']}/{sid}"
                if c is None:
                    errors.append(f"{where}: cell missing")
                    continue
                band = CHANCE_BANDS.get(c["rating"])
                if band and c["chance"] is not None and not band[0] <= c["chance"] <= band[1]:
                    errors.append(f"{where}: chance {c['chance']} outside {c['rating']} band {band[0]}–{band[1]}")
                for w in [(c.get("wind") or {}).get("launch")] + list((c.get("wind") or {}).get("aloft") or []):
                    if not w:
                        continue
                    sp = w.get("speed_kt")
                    top = max(sp) if isinstance(sp, list) else sp
                    if top is not None and top > 120:
                        errors.append(f"{where}: implausible wind speed {sp} kt")
            extra = set(s["cells"]) - set(slot_ids)
            if extra:
                errors.append(f"{g['id']}/{s['id']}: cells for unknown slots {sorted(extra)}")

    allowed = known_urls(raw)
    for u in sorted(set(report_urls(report))):
        if u not in allowed:
            errors.append(f"unknown URL (not in raw data or repo files): {u}")
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("report")
    ap.add_argument("--raw")
    args = ap.parse_args()
    with open(args.report) as f:
        report = json.load(f)
    raw = None
    if args.raw:
        with open(args.raw) as f:
            raw = json.load(f)
    errors = validate(report, raw, args.report)
    if errors:
        print(f"{len(errors)} error(s):")
        for e in errors:
            print(f"- {e}")
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
