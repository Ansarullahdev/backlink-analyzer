import pandas as pd
from urllib.parse import urlparse
import os

def normalize_url(url):
    """
    Extracts and normalizes the domain from a URL for consistent comparison.
    Converts to lowercase, strips whitespace, and removes 'www.'.
    """
    try:
        url_str = str(url).strip().lower()
        parsed = urlparse(url_str)
        domain = parsed.netloc.replace("www.", "")
        return domain
    except Exception as e:
        print(f"Warning: Could not normalize URL '{url}'. Error: {e}")
        return str(url).strip().lower()

def analyze_backlinks(magis_file, methylated_file, output_file):
    """
    Loads backlink data from two CSV files, normalizes URLs to domain level,
    identifies backlinks present in 'methylated_file' but not in 'magis_file',
    and saves unique domains to a new CSV file.
    """
    print("Starting backlink analysis...")

    if not os.path.exists(magis_file):
        print(f"❌ Error: Magis file not found at '{magis_file}'")
        return
    if not os.path.exists(methylated_file):
        print(f"❌ Error: Methylated file not found at '{methylated_file}'")
        return

    try:
        magis = pd.read_csv(magis_file, skiprows=3)
        print(f"✅ Loaded '{magis_file}' with {len(magis)} rows")
    except Exception as e:
        print(f"❌ Error loading '{magis_file}': {e}")
        return

    try:
        methylated = pd.read_csv(methylated_file, skiprows=4)
        print(f"✅ Loaded '{methylated_file}' with {len(methylated)} rows")
    except Exception as e:
        print(f"❌ Error loading '{methylated_file}': {e}")
        return

    magis_expected_cols = ["#", "Col2", "Col3", "NO", "ANCHOR", "BACKLINKS", "DA", "WEBSITE"]
    if len(magis.columns) == len(magis_expected_cols):
        magis.columns = magis_expected_cols
    else:
        print(f"⚠️ Column mismatch in '{magis_file}', columns found: {list(magis.columns)}")

    methylated_expected_cols = ["#", "Col2", "Col3", "NO", "WEBSITE", "ANCHOR", "BACKLINKS", "DA"]
    if len(methylated.columns) == len(methylated_expected_cols):
        methylated.columns = methylated_expected_cols
    else:
        print(f"⚠️ Column mismatch in '{methylated_file}', columns found: {list(methylated.columns)}")

    try:
        magis["normalized"] = magis["BACKLINKS"].apply(normalize_url)
    except KeyError:
        print(f"❌ 'BACKLINKS' column missing in '{magis_file}'")
        return

    try:
        methylated["normalized"] = methylated["BACKLINKS"].apply(normalize_url)
    except KeyError:
        print(f"❌ 'BACKLINKS' column missing in '{methylated_file}'")
        return

    print("🔍 Domains normalized.")

    filtered = methylated[~methylated["normalized"].isin(magis["normalized"])]
    print(f"🔎 Found {len(filtered)} unique domains in methylated not in magis.")

    try:
        filtered[["BACKLINKS", "DA"]].to_csv(output_file, index=False)
        print(f"✅ Saved unique backlinks to '{output_file}'")
    except KeyError:
        print("❌ Columns 'BACKLINKS' or 'DA' not found.")
    except Exception as e:
        print(f"❌ Error saving file '{output_file}': {e}")

if __name__ == "__main__":
    # Update these filenames if your files are in another folder
    magis_csv_file = "Magis_Tv.csv"
    methylated_csv_file = "Methylated_B12.csv"
    output_csv_file = "backlinks_to_use_for_magis.csv"

    analyze_backlinks(magis_csv_file, methylated_csv_file, output_csv_file)
