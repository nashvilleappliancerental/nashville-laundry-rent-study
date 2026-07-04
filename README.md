# Nashville in-unit laundry rent premium — study

An open, reproducible estimate of **how much more rent is associated with having
in-unit laundry** in Nashville rental listings, producing a citable headline like:

> *In-unit laundry is associated with about $X more per month.*

**This is an association, not a cause.** See the honesty note below.

---

## What this repo is

- `data/template.csv` — the empty data table to fill in (one row per listing).
- `data/README.md` — the data dictionary (every field, allowed values, sampling notes).
- `analysis/hedonic.py` — the analysis: cleans the data and runs the regression.
- `analysis/hedonic.ipynb` — the same analysis as a Google Colab notebook (no install needed).
- Charts: in-unit premium by area, and share of listings with in-unit laundry by price tier.

## The honesty note (please read before citing)

This study reports an **associational** estimate, not a causal one. Using a
standard hedonic (feature-based) rent regression, it compares advertised listings
that are similar in **bedrooms, bathrooms, square footage, property type, and
area**, and asks how much more the ones with in-unit laundry are advertised for.

That adjusts for the obvious differences, but **not** for everything. Units with
in-unit laundry may also be newer, nicer, or better managed in ways this data
does not capture. So the honest reading is:

> Listings with in-unit laundry advertise about $X more per month than
> otherwise-similar listings **in this sample** — an association, not proof that
> laundry *causes* higher rent.

We report a **95% confidence interval** on every number and avoid false precision.

## Sample frame (what the data does and doesn't represent)

- The rows are **actively advertised listings** from a defined source (ideally a
  single rental portal over a defined window).
- That is a snapshot of what's **on the market**, not a census of all housing
  stock, and it reflects one portal's coverage and how landlords describe units.
- It is collected **manually**, so it's a modest sample — treat the headline as a
  reasonable estimate with a stated confidence range, not a definitive figure.

Document exactly what you collected (portal, dates, filters) so anyone can
reproduce it.

## Method

A log-linear hedonic regression (ordinary least squares) with
heteroskedasticity-robust (HC3) standard errors:

```
log(rent) ~ bedrooms + bathrooms + sqft + C(property_type) + C(area) + in_unit
```

- `in_unit` is a 0/1 flag (1 when `laundry == in_unit`).
- Because rent is logged, the `in_unit` coefficient is a **percent** premium; we
  convert it to **dollars at the sample's median rent** for a plain-English number.
- A **plain dollar model** (`rent ~ …`, not logged) is run as a cross-check, where
  the `in_unit` coefficient is already in dollars per month.

Cleaning: drop rows missing any key field; keep valid category values; trim rent
to **$400–$6,000** to remove obvious data-entry errors.

## How to run it (Google Colab — no install, browser only)

1. Open **`analysis/hedonic.ipynb`** in Google Colab
   (in Colab: *File → Open notebook → GitHub*, paste this repo's URL).
2. Run the cells top to bottom. The first run uses **synthetic demo data** so you
   can see the whole pipeline work immediately.
3. When you've filled in `data/template.csv` and committed it, switch the run cell
   to your real data (instructions are in the notebook) and re-run.

### Run it locally instead (optional)

```bash
pip install -r requirements.txt
python analysis/hedonic.py --demo                 # synthetic test run
python analysis/hedonic.py --data data/template.csv   # your data
```

## Reproducibility

Dependencies are minimal: `pandas`, `numpy`, `statsmodels`, `matplotlib`
(see `requirements.txt`). The demo data is generated from a fixed random seed, so
demo runs are identical for everyone.

## License

[MIT](LICENSE). Open data, open method — reuse and check our work.
