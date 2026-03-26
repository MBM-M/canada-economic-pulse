"""
fetch_data.py
-------------
Downloads raw CSVs from the StatCan Web Data Service and saves them locally.
Run this once before opening the Jupyter notebook.
 
Tables used:
  14-10-0023-01  Employment by industry (seasonally adjusted)
  18-10-0005-01  CPI - All-items + shelter component, by province
  14-10-0064-01  Average hourly wages by province and job type
"""
 
import os
import zipfile
import io
import requests
 
# Resolve RAW_DIR relative to this script's location, not cwd
RAW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw")
os.makedirs(RAW_DIR, exist_ok=True)
 
# Step 1: Ask the WDS API for the real ZIP URL
WDS_URL = "https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/{pid}/en"
 
TABLES = {
    "employment":  "14100023",   # 14-10-0023-01 Employment by industry
    "cpi":         "18100005",   # 18-10-0005-01 CPI all-items + shelter
    "wages":       "14100064",   # 14-10-0064-01 Average hourly wages by province
}
 
 
def download_table(name: str, pid: str) -> None:
    """Download a StatCan table ZIP and extract the main CSV."""
    out_path = os.path.join(RAW_DIR, f"{name}.csv")
    if os.path.exists(out_path):
        print(f"  [skip] {name}.csv already exists")
        return
 
    print(f"  Downloading {name} (pid={pid}) ...", end=" ", flush=True)
 
    # Step 1: get the actual ZIP download URL from the WDS API
    api_url = WDS_URL.format(pid=pid)
    api_resp = requests.get(api_url, timeout=30)
    api_resp.raise_for_status()
    zip_url = api_resp.json()["object"]
 
    # Step 2: download the ZIP
    r = requests.get(zip_url, timeout=180)
    r.raise_for_status()
 
    # The ZIP contains <pid>-eng.csv (data) and <pid>-eng_MetaData.csv
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        csv_name = next(n for n in z.namelist() if n.endswith(".csv") and "MetaData" not in n)
        with z.open(csv_name) as f:
            content = f.read()
 
    with open(out_path, "wb") as f:
        f.write(content)
 
    size_mb = len(content) / 1_048_576
    print(f"done ({size_mb:.1f} MB)")
 
 
if __name__ == "__main__":
    print("Fetching StatCan datasets...\n")
    for name, pid in TABLES.items():
        download_table(name, pid)
        print(name, pid)
    print("\nAll datasets saved to data/raw/")