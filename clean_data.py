"""
clean_data.py
-------------
Reads raw StatCan CSVs, cleans and filters them, and saves
analysis-ready CSVs to data/processed/.

Run after fetch_data.py.
"""

import os
import sys
import pandas as pd

RAW_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw")
PROC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "processed")
os.makedirs(PROC_DIR, exist_ok=True)

PROVINCES = [
    "British Columbia", "Alberta", "Saskatchewan", "Manitoba",
    "Ontario", "Quebec", "New Brunswick", "Nova Scotia",
    "Prince Edward Island", "Newfoundland and Labrador",
]

START_YEAR = 2014
END_YEAR   = 2024


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def load_raw(name: str) -> pd.DataFrame:
    path = os.path.join(RAW_DIR, f"{name}.csv")
    df = pd.read_csv(path, low_memory=False)
    df.columns = df.columns.str.strip()
    return df


def inspect(name: str) -> None:
    df = load_raw(name)
    print(f"\n=== {name} columns ===")
    print(df.columns.tolist())
    # Print unique values for every non-metadata column
    skip = {"REF_DATE","GEO","DGUID","UOM","UOM_ID","SCALAR_FACTOR","SCALAR_ID",
            "VECTOR","COORDINATE","VALUE","STATUS","SYMBOL","TERMINATED","DECIMALS"}
    for col in df.columns:
        if col not in skip:
            print(f"  [{col}]: {df[col].unique()[:12]}")


def parse_ref_date(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Handle both YYYY-MM and YYYY formats
    df["REF_DATE"] = pd.to_datetime(df["REF_DATE"].astype(str), format="mixed", dayfirst=False)
    df["year"]  = df["REF_DATE"].dt.year
    df["month"] = df["REF_DATE"].dt.month
    return df


def filter_years(df: pd.DataFrame) -> pd.DataFrame:
    return df[(df["year"] >= START_YEAR) & (df["year"] <= END_YEAR)].copy()


# ─────────────────────────────────────────────
# 1. Employment by industry  (14-10-0023-01)
# ─────────────────────────────────────────────

def clean_employment() -> None:
    print("Cleaning employment data...")
    df = load_raw("employment")
    df = parse_ref_date(df)
    df = filter_years(df)

    print(f"  Rows after year filter: {len(df):,}")
    print(f"  GEO sample: {df['GEO'].unique()[:5]}")

    mask = (
        (df["GEO"] == "Canada") &
        (df["Labour force characteristics"] == "Employment") &
        (df["Gender"] == "Total - Gender") &
        (df["Age group"] == "15 years and over")
    )
    df = df[mask][["REF_DATE", "year", "month",
                   "North American Industry Classification System (NAICS)",
                   "VALUE"]].copy()
    df.columns = ["date", "year", "month", "industry", "employed_thousands"]
    df = df.dropna(subset=["employed_thousands"])

    if df.empty:
        print("  WARNING: Still empty after filter — run inspect to debug.")
        return

    annual = (
        df.groupby(["year", "industry"])["employed_thousands"]
        .mean()
        .reset_index()
        .rename(columns={"employed_thousands": "avg_employed_thousands"})
    )

    df.to_csv(os.path.join(PROC_DIR, "employment_monthly.csv"), index=False)
    annual.to_csv(os.path.join(PROC_DIR, "employment_annual.csv"), index=False)
    print(f"  Saved employment_monthly.csv  ({len(df):,} rows)")
    print(f"  Saved employment_annual.csv   ({len(annual):,} rows)")


# ─────────────────────────────────────────────
# 2. CPI  (18-10-0005-01)
#    We want "All-items" and the shelter component.
#    Print all unique product names so we can find the right shelter label.
# ─────────────────────────────────────────────

def clean_cpi() -> None:
    print("Cleaning CPI data...")
    df = load_raw("cpi")
    df = parse_ref_date(df)
    df = filter_years(df)

    prod_col = "Products and product groups"
    all_products = df[prod_col].unique()

    # Find shelter-related label dynamically
    shelter_candidates = [p for p in all_products if "shelter" in p.lower()
                          or "housing" in p.lower() or "accommodation" in p.lower()]
    print(f"  Shelter candidates: {shelter_candidates}")

    if not shelter_candidates:
        print("  ERROR: No shelter/housing product found. All products:")
        print(" ", all_products)
        return

    shelter_label = shelter_candidates[0]
    print(f"  Using shelter label: '{shelter_label}'")

    components = ["All-items", shelter_label]
    mask = (
        (df[prod_col].isin(components)) &
        (df["GEO"].isin(["Canada"] + PROVINCES)) &
        (df["UOM"] == "2002=100")   # Use the standard 2002-base index, not 1992
    )
    df = df[mask][["REF_DATE", "year", "month", "GEO", prod_col, "VALUE"]].copy()
    df.columns = ["date", "year", "month", "geo", "component", "cpi"]
    # Normalize component name so shelter is always called "Shelter"
    df["component"] = df["component"].apply(
        lambda x: "Shelter" if x != "All-items" else "All-items"
    )
    df = df.dropna(subset=["cpi"])

    if df.empty:
        print("  WARNING: No rows matched CPI filter after UOM filter.")
        print("  UOM values:", load_raw("cpi")["UOM"].unique())
        return

    annual = (
        df.groupby(["year", "geo", "component"])["cpi"]
        .mean()
        .reset_index()
        .rename(columns={"cpi": "avg_cpi"})
    )

    df.to_csv(os.path.join(PROC_DIR, "cpi_monthly.csv"), index=False)
    annual.to_csv(os.path.join(PROC_DIR, "cpi_annual.csv"), index=False)
    print(f"  Saved cpi_monthly.csv   ({len(df):,} rows)")
    print(f"  Saved cpi_annual.csv    ({len(annual):,} rows)")


# ─────────────────────────────────────────────
# 3. Wages  (14-10-0064-01)
#    Columns: Wages, Type of work, NAICS, Gender, Age group
#    Filter: average hourly wages, all industries, total gender, 15+
# ─────────────────────────────────────────────

def clean_wages() -> None:
    print("Cleaning wages data...")
    df = load_raw("wages")
    df = parse_ref_date(df)
    df = filter_years(df)

    # Show what's in the Wages column
    print(f"  'Wages' unique values: {df['Wages'].unique()[:10]}")
    print(f"  'Type of work' unique: {df['Type of work'].unique()[:6]}")

    # Find the average hourly wage label
    wages_col_vals = df["Wages"].unique()
    hourly_label = next(
        (v for v in wages_col_vals if "average hourly" in v.lower()),
        None
    )
    if hourly_label is None:
        print("  WARNING: No 'average hourly' wage label found. Using first available:")
        hourly_label = wages_col_vals[0]
    print(f"  Using wages label: '{hourly_label}'")

    mask = (
        (df["GEO"].isin(["Canada"] + PROVINCES)) &
        (df["Wages"] == hourly_label) &
        (df["Type of work"] == "Both full- and part-time employees") &
        (df["Gender"] == "Total - Gender") &
        (df["Age group"] == "15 years and over") &
        (df["North American Industry Classification System (NAICS)"]
            .str.contains("Total employees, all industries", na=False))
    )
    df = df[mask][["REF_DATE", "year", "month", "GEO", "VALUE"]].copy()
    df.columns = ["date", "year", "month", "geo", "avg_hourly_wage"]
    df = df.dropna(subset=["avg_hourly_wage"])

    if df.empty:
        print("  WARNING: No rows matched wages filter.")
        return

    annual = (
        df.groupby(["year", "geo"])["avg_hourly_wage"]
        .mean()
        .reset_index()
    )

    df.to_csv(os.path.join(PROC_DIR, "wages_monthly.csv"), index=False)
    annual.to_csv(os.path.join(PROC_DIR, "wages_annual.csv"), index=False)
    print(f"  Saved wages_monthly.csv   ({len(df):,} rows)")
    print(f"  Saved wages_annual.csv    ({len(annual):,} rows)")


# ─────────────────────────────────────────────
# 4. Merged dataset
# ─────────────────────────────────────────────

def build_merged() -> None:
    print("Building merged wages + CPI dataset...")

    wages_path = os.path.join(PROC_DIR, "wages_annual.csv")
    cpi_path   = os.path.join(PROC_DIR, "cpi_annual.csv")

    if not os.path.exists(wages_path) or not os.path.exists(cpi_path):
        print("  SKIP: wages_annual.csv or cpi_annual.csv missing — fix earlier errors first.")
        return

    wages = pd.read_csv(wages_path)
    cpi   = pd.read_csv(cpi_path)

    cpi_pivot = cpi.pivot_table(
        index=["year", "geo"], columns="component", values="avg_cpi"
    ).reset_index()
    cpi_pivot.columns = ["year", "geo", "cpi_all_items", "cpi_shelter"]

    merged = wages.merge(cpi_pivot, on=["year", "geo"], how="inner")

    if merged.empty:
        print("  WARNING: Merged dataset is empty — check that geo values match between wages and CPI.")
        print("  Wages GEOs:", wages["geo"].unique())
        print("  CPI GEOs:", cpi["geo"].unique())
        return

    base = merged[merged["year"] == START_YEAR][
        ["geo", "avg_hourly_wage", "cpi_all_items", "cpi_shelter"]
    ].copy()
    base.columns = ["geo", "wage_base", "cpi_base", "shelter_base"]
    merged = merged.merge(base, on="geo", how="left")

    merged["wage_index"]    = (merged["avg_hourly_wage"] / merged["wage_base"])   * 100
    merged["cpi_index"]     = (merged["cpi_all_items"]  / merged["cpi_base"])     * 100
    merged["shelter_index"] = (merged["cpi_shelter"]    / merged["shelter_base"]) * 100

    merged.drop(columns=["wage_base", "cpi_base", "shelter_base"], inplace=True)
    merged.to_csv(os.path.join(PROC_DIR, "wages_vs_cpi.csv"), index=False)
    print(f"  Saved wages_vs_cpi.csv  ({len(merged):,} rows)")


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "inspect":
        for name in ("employment", "cpi", "wages"):
            inspect(name)
        sys.exit()

    print("=" * 50)
    print("StatCan Data Cleaner")
    print("=" * 50)
    clean_employment()
    print()
    clean_cpi()
    print()
    clean_wages()
    print()
    build_merged()
    print("\nDone! Processed files are in data/processed/")