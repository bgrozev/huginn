"""Add a validated report to the site: latest.json and the history index.

Usage: python3 scripts/publish.py site/reports/<run-id>.json [--commit <sha>]
"""
import argparse
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS = os.path.join(ROOT, "site", "reports")


def summary(report):
    """One line for the history list: the best go slots, or that there are none."""
    labels = {s["id"]: s["label"] for s in report["slots"]}
    best = []
    for g in report["groups"]:
        for s in g["spots"]:
            for sid, c in s["cells"].items():
                if c["rating"] == "go":
                    best.append((c.get("chance") or 0, f"{s['name']} {labels.get(sid, sid)}"))
    if not best:
        return "No go slots"
    best.sort(reverse=True)
    return "Go: " + ", ".join(name for _, name in best[:3])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("report")
    ap.add_argument("--commit")
    args = ap.parse_args()

    with open(args.report) as f:
        report = json.load(f)
    if args.commit:
        report.setdefault("run", {})["commit"] = args.commit
        with open(args.report, "w") as f:
            json.dump(report, f, indent=1, ensure_ascii=False)

    with open(os.path.join(REPORTS, "latest.json"), "w") as f:
        json.dump(report, f, indent=1, ensure_ascii=False)

    index_path = os.path.join(REPORTS, "index.json")
    try:
        with open(index_path) as f:
            index = json.load(f)
    except FileNotFoundError:
        index = {"reports": []}
    # The sample is a layout preview; it leaves the history once real reports exist.
    entries = [r for r in index["reports"] if r["id"] not in (report["id"], "sample")]
    entries.insert(0, {"id": report["id"], "generated_at": report["generated_at"], "summary": summary(report)})
    entries.sort(key=lambda r: r["generated_at"], reverse=True)
    with open(index_path, "w") as f:
        json.dump({"reports": entries}, f, indent=1, ensure_ascii=False)
    print(f"published {report['id']}: {entries[0]['summary']}")


if __name__ == "__main__":
    main()
