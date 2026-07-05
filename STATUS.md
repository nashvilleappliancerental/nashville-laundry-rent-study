# STATUS — Nashville In-Unit Laundry Rent Premium Study

> **Read this first.** Single source of truth for where the project stands so any
> agent or person can jump in. Last updated: 2026-07-04.

## ⚠️ Before you end a session — UPDATE THIS FILE
Any agent or person working on this project **must update `STATUS.md` before
stopping** — this is how Claude ↔ Codex ↔ the owner stay in sync, and a stale
STATUS breaks the handoff. Specifically:
1. Move finished items from **TODO → Done**, and add any new tasks you discovered.
2. Bump the **Last updated** date above.
3. Record any new decisions or guardrails.
4. Commit it: `git add STATUS.md && git commit -m "Update STATUS"`.

If you're a fresh agent: read this whole file first, then start.

## What this is
An open, reproducible hedonic-regression study estimating **how much more Nashville
rent is associated with in-unit laundry**, producing a citable headline ("in-unit
laundry ≈ $X more per month"). It's a **content/backlink asset for Nashville
Appliance Rental** — a washer/dryer rental business — not just an academic exercise.
Public repo, MIT, "open data, open method." Explicitly **associational, not causal**
(see the honesty note in README).

## Where things live
- `data/listings.csv` — the collected dataset (one row per listing).
- `data/template.csv` — empty schema example; `data/README.md` — data dictionary.
- `analysis/hedonic.py` / `analysis/hedonic.ipynb` — the regression (Colab-runnable).
- `README.md` — method, honesty note, how to run.
- Repo: `github.com/nashvilleappliancerental/nashville-laundry-rent-study`, branch `main`.

## Current state — DONE
- Study scaffolded: schema, data dictionary, hedonic OLS (log-linear + dollar
  cross-check, HC3 SEs), Colab notebook with synthetic-demo fallback.
- **First 6 listings collected** manually from Apartments.com (commit `edbfdb3`).
  `laundry` field values in use: `in_unit`, `hookups`.

## NOT done — open gates
- **Sample far too small (n=6).** Need at least a few hundred listings — and more
  **non-`in_unit`** rows specifically — before the headline estimate is credible.
- Collection is **manual paste-to-CSV**; no scraper. This is the main bottleneck.

## Content-asset backlog (WHY this study matters — from 2026-07-04 strategy chat)
The owner wants more linkable/traffic assets for Nashville Appliance Rental beyond
the existing **rent-vs-buy calculator** and this study. Key realization: several
proposed assets are **byproducts of scaling THIS dataset**, because the `laundry`
column already distinguishes `in_unit` vs `hookups`:

- **"Nashville apartments with hookups but no machines" list/directory** — a
  *lead-gen / conversion* asset (these renters are the exact customer). Low backlink
  value on its own, high commercial intent. = the `laundry == hookups` rows.
- **Aggregate stat** ("X% of Antioch 1BRs have hookups only") = the *backlink* asset
  a journalist/finance blog cites. Same collection, second output.
- **Nashville "laundry map"** (share of in-unit vs hookups vs none by neighborhood) —
  most linkable (visual + local + original); likely needs extra fields beyond the
  current rent schema.
- Data availability: Apartments.com/Zillow/Apartment List *filter* in-unit vs
  hookups but offer **no clean download** — must be harvested listing-by-listing.
  Owner's **own delivery/customer records** are the best proprietary, ground-truth
  source and should seed/validate the list.
- Calculators/guides (laundromat-vs-in-unit-vs-rent, move-it-or-rent, landlord-ROI)
  would ship on the main site (`nashville-astro`), not here.

## TODO (ordered)
- [ ] **DEFERRED (owner has no time now):** scale data collection from 6 → a few
      hundred listings; prioritize non-`in_unit` rows. Consider a cleaner
      scrape/paste workflow vs. pure manual.
- [ ] Once n is adequate, re-run `hedonic.py` and lock the headline + 95% CI.
- [ ] Derive the "hookups but no machines" list + the aggregate neighborhood stat.
- [ ] Seed/cross-check against the owner's own delivery history for authority.
- [ ] Decide whether the "laundry map" needs a separate collection (extra fields).

## Decisions / guardrails (don't violate)
- **Associational, not causal** — never overclaim. Always report the 95% CI; avoid
  false precision. Keep the README honesty note intact.
- Document sampling frame (portal, dates, filters) for reproducibility.
- Cleaning rules: drop rows missing key fields; trim rent to $400–$6,000.
- Never fabricate data rows — real listings only.

## Build / run
```
# Colab (no install): open analysis/hedonic.ipynb via File > Open notebook > GitHub
pip install -r requirements.txt
python analysis/hedonic.py --demo                      # synthetic test run
python analysis/hedonic.py --data data/listings.csv    # real collected data
```
