# TODO

Feature backlog. Architecture and phases: [PLAN.md](PLAN.md).

- [ ] **Send feedback** — after flying, report what happened per spot/slot (flew? matched the
      forecast? surprises?). Likely a GitHub issue form linked from the detail panel.
- [ ] **Alerts** — notify me when a spot looks good, e.g. "Cherry is Go tomorrow AM". Per-spot
      subscriptions, threshold on rating/chance.
- [x] **Measure a run's share of the Pro 5-hour limit** (2026-11-06, Opus 5.5, local run): 27 turns,
      6 min, 43k output / 174k cache-write / 1.63M cache-read tokens → 5-hour window 57% → 66%
      (~9 points, includes a few small turns of the measuring session), weekly 13% → 14%.
      An earlier CI run used a third of the cache reads (10 turns) → likely ~4–5 points.
      Daily is affordable (~1% of the weekly limit per run).
- [ ] **Cut agent turns** — add a per-slot summary to the raw data (wind ranges at launch, aloft,
      precipitation) so the agent doesn't spend turns exploring the raw file; it tried twice to
      inspect it with Python (blocked).
- [ ] Bring back the map (hidden for now, `SHOW_MAP` in `site/assets/huginn.js`).
- [ ] Bring back the group selector once there is more than one group (automatic).
