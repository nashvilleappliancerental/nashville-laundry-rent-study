#!/usr/bin/env python3
"""
Hedonic rent regression: the in-unit laundry premium in Nashville.

=============================== READ THIS FIRST ==============================
This estimates how much MORE rent is *associated with* having in-unit laundry,
after adjusting for bedrooms, bathrooms, square footage, property type, and area.

It is an ASSOCIATIONAL estimate, NOT a causal one. Listings with in-unit laundry
may differ from others in ways this data does not measure (newer construction,
nicer finishes, better management, etc.). So read the result as:

    "Listings with in-unit laundry advertise about $X more per month than
     otherwise-similar listings in this sample."

NOT as "adding laundry causes rent to rise by $X."
=============================================================================

Usage (browser-friendly; runs in Google Colab):
    python analysis/hedonic.py --demo                 # synthetic data, to test
    python analysis/hedonic.py --data data/template.csv   # your collected data
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

# --- Configuration -----------------------------------------------------------
DEFAULT_DATA = "data/template.csv"
RENT_MIN, RENT_MAX = 400, 6000  # trim implausible rents (data-entry errors)
KEY_FIELDS = ["rent", "bedrooms", "bathrooms", "sqft", "property_type", "area", "laundry"]
VALID_PROPERTY = {"apartment", "condo", "townhome", "house"}
VALID_LAUNDRY = {"in_unit", "hookups", "shared", "none"}

# The hedonic models. in_unit is a 0/1 flag derived from laundry == "in_unit".
FORMULA_LOG = "log_rent ~ bedrooms + bathrooms + sqft + C(property_type) + C(area) + in_unit"
FORMULA_DOLLAR = "rent ~ bedrooms + bathrooms + sqft + C(property_type) + C(area) + in_unit"


# --- Data ------------------------------------------------------------------
def clean_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Clean a raw listings frame: coerce types, normalize categories, trim rent."""
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]

    for col in ["rent", "bedrooms", "bathrooms", "sqft"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in ["property_type", "laundry"]:
        df[col] = df[col].astype(str).str.strip().str.lower()
    df["area"] = df["area"].astype(str).str.strip().str.title()

    # Drop rows missing any key field.
    df = df.dropna(subset=KEY_FIELDS)
    # Keep only valid category values.
    df = df[df["property_type"].isin(VALID_PROPERTY)]
    df = df[df["laundry"].isin(VALID_LAUNDRY)]
    # Trim rent to a plausible band.
    df = df[(df["rent"] >= RENT_MIN) & (df["rent"] <= RENT_MAX)]

    df["in_unit"] = (df["laundry"] == "in_unit").astype(int)
    df["log_rent"] = np.log(df["rent"])
    return df.reset_index(drop=True)


def load_and_clean(path: str):
    raw = pd.read_csv(path)
    return clean_frame(raw), len(raw)


def fit(formula: str, df: pd.DataFrame):
    """OLS with HC3 heteroskedasticity-robust standard errors."""
    return smf.ols(formula, data=df).fit(cov_type="HC3")


# --- Reporting -------------------------------------------------------------
def report(df: pd.DataFrame, n_raw: int):
    print("=" * 74)
    print(" IN-UNIT LAUNDRY RENT PREMIUM - Nashville  (ASSOCIATIONAL, not causal)")
    print("=" * 74)
    print(f"Rows in file:             {n_raw}")
    print(f"Rows used after cleaning: {len(df)}   "
          f"(dropped missing key fields; rent trimmed to ${RENT_MIN}-${RENT_MAX})")
    print()
    print("Laundry type counts (cleaned sample):")
    print(df["laundry"].value_counts().to_string())
    print(f"\nin_unit = 1 for {int(df['in_unit'].sum())} of {len(df)} listings "
          f"({df['in_unit'].mean():.1%} of the sample)")
    print()

    if len(df) < 30 or df["in_unit"].nunique() < 2:
        print("Not enough data for a stable estimate yet (need at least ~30 rows "
              "AND both in-unit and non-in-unit listings present). Add more listings.")
        return None

    log_res = fit(FORMULA_LOG, df)
    print("-" * 74)
    print("LOG-LINEAR HEDONIC MODEL  ->  log(rent) ~ size + type + area + in_unit")
    print("HC3 robust standard errors")
    print("-" * 74)
    print(log_res.summary())

    # In a log-linear model, the in_unit coefficient is an approximate percent
    # premium; exp(beta) - 1 is the exact percent. Convert to dollars at the
    # sample median rent so it is easy to cite.
    beta = log_res.params["in_unit"]
    lo, hi = log_res.conf_int().loc["in_unit"]
    pct, pct_lo, pct_hi = np.exp(beta) - 1, np.exp(lo) - 1, np.exp(hi) - 1
    med = df["rent"].median()

    print("\n" + "-" * 74)
    print("IN-UNIT LAUNDRY PREMIUM")
    print("-" * 74)
    print(f"Sample median rent:  ${med:,.0f}")
    print(f"Percent premium:     {pct:+.1%}   "
          f"(95% CI {pct_lo:+.1%} to {pct_hi:+.1%})")
    print(f"Dollar premium at median rent:  ${med * pct:,.0f}   "
          f"(95% CI ${med * pct_lo:,.0f} to ${med * pct_hi:,.0f})")

    # Plain dollar model as a cross-check: the in_unit coefficient is already
    # in dollars/month, no transformation needed.
    dol_res = fit(FORMULA_DOLLAR, df)
    d_beta = dol_res.params["in_unit"]
    d_lo, d_hi = dol_res.conf_int().loc["in_unit"]
    print("\nCross-check - plain dollar model (rent in $, not logged):")
    print(f"Dollar premium:  ${d_beta:,.0f}   (95% CI ${d_lo:,.0f} to ${d_hi:,.0f})")

    print("\n" + "-" * 74)
    print("HEADLINE (associational):")
    print(f"  In-unit laundry is associated with about ${med * pct:,.0f} more per")
    print(f"  month (95% CI ${med * pct_lo:,.0f} to ${med * pct_hi:,.0f}) than")
    print("  otherwise-similar listings in this sample. This is an association,")
    print("  not proof that laundry causes higher rent.")
    print("-" * 74)
    return log_res


# --- Charts ----------------------------------------------------------------
def chart_premium_by_area(df, outpath="charts/premium_by_area.png", min_n=15):
    """In-unit dollar premium estimated separately within each area (95% CI)."""
    import matplotlib.pyplot as plt

    rows = []
    for area, g in df.groupby("area"):
        if len(g) < min_n or g["in_unit"].nunique() < 2:
            continue
        try:
            r = smf.ols(
                "log_rent ~ bedrooms + bathrooms + sqft + C(property_type) + in_unit",
                data=g,
            ).fit(cov_type="HC3")
        except Exception:
            continue
        b = r.params["in_unit"]
        lo, hi = r.conf_int().loc["in_unit"]
        med = g["rent"].median()
        prem = med * (np.exp(b) - 1)
        plo, phi = med * (np.exp(lo) - 1), med * (np.exp(hi) - 1)
        rows.append((f"{area}\n(n={len(g)})", prem, prem - plo, phi - prem))

    if not rows:
        print("Premium-by-area chart skipped: no area has enough data yet "
              f"(need >= {min_n} listings with both laundry types).")
        return

    labels, prem, elo, ehi = zip(*rows)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(labels, prem, yerr=[elo, ehi], capsize=4, color="#4C72B0")
    ax.axhline(0, color="#888", lw=0.8)
    ax.set_ylabel("Estimated in-unit premium ($/month)")
    ax.set_title("In-unit laundry premium by area (associational; 95% CI)\n"
                 "Per-area samples are small - read as rough, not precise")
    plt.tight_layout()
    fig.savefig(outpath, dpi=120)
    plt.show()
    print(f"Saved {outpath}")


def chart_share_by_tier(df, outpath="charts/inunit_share_by_tier.png", tiers=4):
    """Share of listings with in-unit laundry, by rent quartile."""
    import matplotlib.pyplot as plt

    d = df.copy()
    d["tier"] = pd.qcut(d["rent"], tiers, duplicates="drop")
    share = d.groupby("tier", observed=True)["in_unit"].mean()
    labels = [f"${int(iv.left):,}-${int(iv.right):,}" for iv in share.index]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(labels, share.values * 100, color="#55A868")
    ax.set_ylabel("Share with in-unit laundry (%)")
    ax.set_xlabel("Rent tier")
    ax.set_title("Share of listings with in-unit laundry, by price tier")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    fig.savefig(outpath, dpi=120)
    plt.show()
    print(f"Saved {outpath}")


# --- Synthetic demo data (clearly fake; only to test the pipeline) ----------
def make_demo(n=250, seed=7) -> pd.DataFrame:
    """Generate SYNTHETIC listings with a built-in in-unit premium (~10%).

    This is fake data for exercising the code end to end. It is NOT a real
    observation of the Nashville market and must never be cited.
    """
    rng = np.random.default_rng(seed)
    areas = ["Downtown/Core", "East Nashville", "South Nashville",
             "West Nashville", "North Nashville", "Southeast/Antioch"]
    ptypes = ["apartment", "condo", "townhome", "house"]
    laundry_opts = ["in_unit", "hookups", "shared", "none"]

    beds = rng.integers(0, 4, n)
    baths = np.clip(np.round((beds * 0.6 + rng.normal(1.0, 0.4, n)) * 2) / 2, 1, 3.5)
    sqft = (400 + beds * 350 + rng.normal(0, 120, n)).clip(300, 2500).round()
    ptype = rng.choice(ptypes, n, p=[0.60, 0.15, 0.15, 0.10])
    area = rng.choice(areas, n)
    laundry = rng.choice(laundry_opts, n, p=[0.45, 0.25, 0.15, 0.15])
    in_unit = (laundry == "in_unit").astype(int)

    area_fx = dict(zip(areas, [0.12, 0.05, 0.03, 0.06, -0.05, -0.08]))
    log_rent = (6.4 + 0.18 * beds + 0.06 * baths + 0.00035 * sqft
                + 0.10 * in_unit                      # <- the planted ~10% premium
                + np.array([area_fx[a] for a in area])
                + rng.normal(0, 0.08, n))
    rent = np.exp(log_rent).round(0).clip(RENT_MIN, RENT_MAX)

    return pd.DataFrame({
        "listing_id": [f"DEMO{i:04d}" for i in range(n)],
        "rent": rent, "bedrooms": beds, "bathrooms": baths, "sqft": sqft,
        "property_type": ptype, "area": area, "laundry": laundry,
        "date_collected": "2026-01-01", "source": "SYNTHETIC_DEMO",
    })


# --- Entry point -----------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(
        description="Hedonic in-unit laundry rent premium (associational, not causal).")
    ap.add_argument("--data", default=DEFAULT_DATA,
                    help="Path to the listings CSV (default: data/template.csv)")
    ap.add_argument("--demo", action="store_true",
                    help="Run on SYNTHETIC demo data to test the pipeline")
    ap.add_argument("--no-charts", action="store_true", help="Skip the charts")
    args = ap.parse_args()

    if args.demo:
        print("\n*** RUNNING ON SYNTHETIC DEMO DATA - NOT REAL OBSERVATIONS ***\n")
        raw = make_demo()
        n_raw = len(raw)
        df = clean_frame(raw)
    else:
        try:
            df, n_raw = load_and_clean(args.data)
        except FileNotFoundError:
            sys.exit(f"CSV not found: {args.data}")
        if n_raw == 0:
            print(f"'{args.data}' has no data rows yet. Fill it in "
                  "(see data/README.md), or run with --demo to test the pipeline.")
            return

    res = report(df, n_raw)
    if res is not None and not args.no_charts:
        os.makedirs("charts", exist_ok=True)
        try:
            chart_premium_by_area(df)
            chart_share_by_tier(df)
        except Exception as e:  # never let a plotting hiccup kill the run
            print(f"(charts skipped: {e})")


if __name__ == "__main__":
    main()
