"""
Copernicus Climate Data Store (CDS) ERA5 Meteorological Data Downloader
Project: A PySpark-Based Big Data Analysis of Air Pollution and Meteorological Patterns in Bengaluru, Karnataka

This script queries the official ECMWF / Copernicus CDS API to retrieve hourly ERA5
reanalysis meteorological data for the Bengaluru metropolitan region matching the
air-quality study period (2024-01-01 to 2025-12-31).

Geographical Bounding Box (Bengaluru):
  North: 13.25, South: 12.75, West: 77.35, East: 77.85
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple

# Paths
BASE_DIR = Path(__file__).resolve().parent
RAW_WEATHER_DIR = BASE_DIR / "raw_weather_data"
RAW_WEATHER_DIR.mkdir(parents=True, exist_ok=True)

CDS_CONFIG_PATH = Path.home() / ".cdsapirc"

# ERA5 Single-Levels Dataset Configuration
DATASET_NAME = "reanalysis-era5-single-levels"

# Required Meteorological Variables
ERA5_VARIABLES = [
    "2m_temperature",
    "2m_dewpoint_temperature",
    "10m_u_component_of_wind",
    "10m_v_component_of_wind",
    "total_precipitation",
    "surface_pressure",
    "total_cloud_cover",
    "boundary_layer_height",
    "surface_solar_radiation_downwards",
]

# Bengaluru Geographical Bounding Box: [North, West, South, East]
BENGALURU_BBOX = [13.25, 77.35, 12.75, 77.85]


def check_cds_credentials() -> bool:
    """
    Checks if CDS API credentials are configured via ~/.cdsapirc or environment variables.
    """
    if CDS_CONFIG_PATH.exists() and CDS_CONFIG_PATH.stat().st_size > 10:
        return True
    if os.environ.get("CDSAPI_URL") and os.environ.get("CDSAPI_KEY"):
        return True
    return False


def setup_cds_credentials(personal_access_token: str) -> None:
    """
    Writes the Copernicus CDS API configuration file ~/.cdsapirc.
    Uses the modern Copernicus Climate Data Store API URL (https://cds.climate.copernicus.eu/api).
    """
    content = f"url: https://cds.climate.copernicus.eu/api\nkey: {personal_access_token.strip()}\n"
    with open(CDS_CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n[SUCCESS] CDS API credentials successfully saved to: {CDS_CONFIG_PATH}")


def print_setup_instructions() -> None:
    """
    Displays clear, step-by-step instructions for registering and obtaining a free CDS API key.
    """
    print("\n" + "=" * 80)
    print("      COPERNICUS CLIMATE DATA STORE (CDS) CREDENTIALS NOT FOUND")
    print("=" * 80)
    print(
        "To download authentic ERA5 reanalysis data directly from ECMWF Copernicus,\n"
        "please follow these quick 3-step setup instructions:\n\n"
        "1. CREATE A FREE ACCOUNT:\n"
        "   Visit: https://cds.climate.copernicus.eu\n"
        "   Click 'Register' and create your free user profile.\n\n"
        "2. ACCEPT THE ERA5 DATASET LICENSE:\n"
        "   Visit: https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=download\n"
        "   Scroll down to the 'Terms of use' section and click 'Accept'.\n\n"
        "3. RETRIEVE YOUR PERSONAL ACCESS TOKEN:\n"
        "   Go to your user profile: https://cds.climate.copernicus.eu/profile\n"
        "   Copy your Personal Access Token (API Key).\n\n"
        "4. CONFIGURE YOUR CREDENTIALS (Choose either option):\n"
        "   Option A - Run this script with the --key parameter:\n"
        "       python download_era5.py --key YOUR_PERSONAL_ACCESS_TOKEN\n\n"
        "   Option B - Manually create the file:\n"
        f"       File path: {CDS_CONFIG_PATH}\n"
        "       Contents:\n"
        "           url: https://cds.climate.copernicus.eu/api\n"
        "           key: <YOUR-PERSONAL-ACCESS-TOKEN>\n"
    )
    print("=" * 80 + "\n")


def build_download_request(years: List[str]) -> dict:
    """
    Constructs the CDS API request dictionary for Bengaluru bounding box and study years.
    """
    return {
        "product_type": ["reanalysis"],
        "variable": ERA5_VARIABLES,
        "year": years,
        "month": [f"{m:02d}" for m in range(1, 13)],
        "day": [f"{d:02d}" for d in range(1, 32)],
        "time": [f"{h:02d}:00" for h in range(24)],
        "data_format": "netcdf",
        "download_format": "unarchived",
        "area": BENGALURU_BBOX,  # North, West, South, East
    }


def download_era5_data(years: List[str] = ["2024", "2025"], split_by_year: bool = True) -> List[Path]:
    """
    Executes the Copernicus CDS API retrieval.
    Downloads NetCDF files for Bengaluru bounding box.
    """
    if not check_cds_credentials():
        print_setup_instructions()
        return []

    try:
        import cdsapi
    except ImportError:
        print("[ERROR] 'cdsapi' library is not installed. Run: pip install cdsapi")
        return []

    client = cdsapi.Client()
    downloaded_files = []

    if split_by_year:
        # Downloading annual chunks ensures faster queueing on ECMWF servers
        for year in years:
            target_file = RAW_WEATHER_DIR / f"bengaluru_era5_{year}.nc"
            if target_file.exists() and target_file.stat().st_size > 1024:
                print(f"[FOUND] {target_file.name} already downloaded ({target_file.stat().st_size:,} bytes). Skipping.")
                downloaded_files.append(target_file)
                continue

            print(f"\n[CDS REQUEST] Submitting ERA5 Reanalysis request for Year: {year}...")
            print(f"  • Bounding Box: {BENGALURU_BBOX} (N, W, S, E)")
            print(f"  • Variables: {len(ERA5_VARIABLES)} surface variables")
            print(f"  • Target File: {target_file}")

            req = build_download_request([year])
            try:
                client.retrieve(DATASET_NAME, req, str(target_file))
                print(f"[SUCCESS] Download completed: {target_file.name} ({target_file.stat().st_size:,} bytes)")
                downloaded_files.append(target_file)
            except Exception as e:
                print(f"[ERROR] Failed to download ERA5 for year {year}: {e}")
    else:
        target_file = RAW_WEATHER_DIR / f"bengaluru_era5_{'_'.join(years)}.nc"
        if target_file.exists() and target_file.stat().st_size > 1024:
            print(f"[FOUND] {target_file.name} already downloaded. Skipping.")
            return [target_file]

        print(f"\n[CDS REQUEST] Submitting ERA5 Reanalysis request for Years: {years}...")
        req = build_download_request(years)
        client.retrieve(DATASET_NAME, req, str(target_file))
        downloaded_files.append(target_file)

    return downloaded_files


def main():
    parser = argparse.ArgumentParser(description="Download ERA5 Meteorological Data for Bengaluru")
    parser.add_argument("--key", type=str, help="Copernicus CDS Personal Access Token (API Key) to configure ~/.cdsapirc")
    parser.add_argument("--years", nargs="+", default=["2024", "2025"], help="Years to download (default: 2024 2025)")
    args = parser.parse_args()

    if args.key:
        setup_cds_credentials(args.key)

    if not check_cds_credentials():
        print_setup_instructions()
        sys.exit(0)

    print(f"Checking credentials... [OK] ({CDS_CONFIG_PATH} verified).")
    download_era5_data(years=args.years, split_by_year=True)


if __name__ == "__main__":
    main()
