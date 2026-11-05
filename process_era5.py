"""
Copernicus ERA5 Meteorological Data Processing, Transformation, and Quality Audit Pipeline
Project: "A PySpark-Based Big Data Analysis of Air Pollution and Meteorological Patterns in Bengaluru, Karnataka"

This script processes NetCDF/GRIB datasets downloaded from Copernicus CDS:
1. Reads NetCDF/GRIB files using xarray and netCDF4.
2. Standardizes units:
   - Temperature & Dewpoint: Kelvin -> Celsius
   - Wind Speed: derived from 10m u & v components (m/s)
   - Wind Direction: meteorological convention (direction FROM which wind blows, 0-360 deg)
   - Relative Humidity: derived via August-Roche-Magnus approximation
   - Total Precipitation: metres -> millimetres
   - Total Cloud Cover: fraction -> percentage
   - Surface Pressure: Pascals -> hectopascals (hPa / mbar)
   - Boundary Layer Height: metres
   - Solar Radiation: J/m2 -> W/m2 (hourly irradiance flux)
3. Preserves original ERA5 variables AND creates separate derived/standardized columns.
4. Generates both UTC and Indian Standard Time (IST, UTC+5:30) timestamps.
5. Maps spatial grid points to the 13 Bengaluru air quality monitoring stations.
6. Exports:
   - bengaluru_era5_weather.csv
   - bengaluru_era5_weather.xlsx
   - weather_data_quality_report.xlsx
"""

import logging
import math
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import pandas as pd
import xarray as xr

# Reconfigure stdout to UTF-8
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("BengaluruERA5Processor")

BASE_DIR = Path(__file__).resolve().parent
RAW_WEATHER_DIR = BASE_DIR / "raw_weather_data"
PROCESSED_WEATHER_DIR = BASE_DIR / "processed_weather_data"
OUTPUT_DIR = BASE_DIR / "output"

RAW_WEATHER_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_WEATHER_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 13 Bengaluru Monitoring Station Coordinates for spatial matching
STATION_COORDINATES = {
    "Bapuji Nagar": {"lat": 12.9641, "lon": 77.5350},
    "BTM Layout": {"lat": 12.9135, "lon": 77.5855},
    "City Railway Station": {"lat": 12.9774, "lon": 77.5681},
    "Hebbal": {"lat": 13.0271, "lon": 77.5891},
    "Hombegowda Nagar": {"lat": 12.9392, "lon": 77.5954},
    "Jayanagar 5th Block": {"lat": 12.9212, "lon": 77.5841},
    "Jigani": {"lat": 12.7842, "lon": 77.6321},
    "Kasturi Nagar": {"lat": 13.0033, "lon": 77.6531},
    "Peenya": {"lat": 13.0270, "lon": 77.5140},
    "RVCE Mailasandra": {"lat": 12.9242, "lon": 77.4990},
    "Sanegurava Halli": {"lat": 12.9922, "lon": 77.5451},
    "Shivapura Peenya": {"lat": 13.0361, "lon": 77.5020},
    "Silk Board": {"lat": 12.9171, "lon": 77.6230},
}


def compute_relative_humidity(temp_c: np.ndarray, dewpoint_c: np.ndarray) -> np.ndarray:
    """
    Computes Relative Humidity (%) from 2m Temperature and 2m Dewpoint Temperature
    using the August-Roche-Magnus approximation:
      e_s(T) = 6.112 * exp((17.67 * T) / (T + 243.5))
      e(Td)  = 6.112 * exp((17.67 * Td) / (Td + 243.5))
      RH     = 100.0 * (e / e_s)
    Clamped to physical range [0.0%, 100.0%].
    """
    a = 17.67
    b = 243.5
    es = 6.112 * np.exp((a * temp_c) / (temp_c + b))
    e = 6.112 * np.exp((a * dewpoint_c) / (dewpoint_c + b))
    rh = 100.0 * (e / es)
    return np.clip(rh, 0.0, 100.0)


def compute_wind_direction(u: np.ndarray, v: np.ndarray) -> np.ndarray:
    """
    Computes meteorological wind direction (in degrees from North, clockwise, 0-360)
    representing the direction FROM which the wind is blowing:
      direction = (atan2(-u, -v) * 180 / pi) % 360
    Convention:
      0 deg   = North (wind blowing from North towards South)
      90 deg  = East  (wind blowing from East towards West)
      180 deg = South (wind blowing from South towards North)
      270 deg = West  (wind blowing from West towards East)
    """
    direction = (np.arctan2(-u, -v) * (180.0 / np.pi)) % 360.0
    return direction


def find_nearest_station(lat: float, lon: float) -> Tuple[str, float]:
    """
    Calculates Haversine distance in km from an ERA5 grid point (lat, lon)
    to the closest Bengaluru air-quality monitoring station.
    """
    R = 6371.0  # Earth radius in km
    min_dist = float("inf")
    nearest_station = ""

    for st_name, coords in STATION_COORDINATES.items():
        st_lat, st_lon = coords["lat"], coords["lon"]
        dlat = math.radians(st_lat - lat)
        dlon = math.radians(st_lon - lon)
        a = (
            math.sin(dlat / 2.0) ** 2
            + math.cos(math.radians(lat)) * math.cos(math.radians(st_lat)) * math.sin(dlon / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        dist = R * c
        if dist < min_dist:
            min_dist = dist
            nearest_station = st_name

    return nearest_station, round(min_dist, 2)


def process_era5_dataset(nc_file: Path) -> pd.DataFrame:
    """
    Loads an ERA5 NetCDF dataset, extracts variables, derives meteorological metrics,
    and returns a standardized tabular DataFrame.
    """
    logger.info("Opening NetCDF file with xarray: %s", nc_file)
    ds = xr.open_dataset(nc_file)

    # Standardize coordinate names across CDS NetCDF conventions
    time_coord = "valid_time" if "valid_time" in ds.coords else "time"
    lat_coord = "latitude" if "latitude" in ds.coords else "lat"
    lon_coord = "longitude" if "longitude" in ds.coords else "lon"

    logger.info("Coordinates detected: time='%s', lat='%s', lon='%s'", time_coord, lat_coord, lon_coord)

    # Convert to pandas DataFrame
    df = ds.to_dataframe().reset_index()

    # Identify variable column names in raw NetCDF (modern vs legacy short names)
    var_map = {}
    for col in df.columns:
        col_lower = col.lower()
        if col_lower in ["t2m", "2t"]:
            var_map["t2m"] = col
        elif col_lower in ["d2m", "2d"]:
            var_map["d2m"] = col
        elif col_lower in ["u10", "10u"]:
            var_map["u10"] = col
        elif col_lower in ["v10", "10v"]:
            var_map["v10"] = col
        elif col_lower in ["sp"]:
            var_map["sp"] = col
        elif col_lower in ["tp"]:
            var_map["tp"] = col
        elif col_lower in ["tcc"]:
            var_map["tcc"] = col
        elif col_lower in ["blh"]:
            var_map["blh"] = col
        elif col_lower in ["ssrd"]:
            var_map["ssrd"] = col

    logger.info("Mapped ERA5 variables: %s", var_map)

    # 1. Timestamps (UTC and IST)
    utc_timestamps = pd.to_datetime(df[time_coord])
    df["Timestamp_UTC"] = utc_timestamps.dt.strftime("%Y-%m-%d %H:%M:%S")
    df["Timestamp_IST"] = (utc_timestamps + pd.Timedelta(hours=5, minutes=30)).dt.strftime("%Y-%m-%d %H:%M:%S")

    # 2. Coordinates
    df["Latitude"] = df[lat_coord].round(4)
    df["Longitude"] = df[lon_coord].round(4)

    # 3. Preserve Original Raw ERA5 Variables
    if "t2m" in var_map:
        df["era5_t2m_k"] = df[var_map["t2m"]]
        df["Temperature_C"] = np.round(df["era5_t2m_k"] - 273.15, 2)
    if "d2m" in var_map:
        df["era5_d2m_k"] = df[var_map["d2m"]]
        df["Dewpoint_C"] = np.round(df["era5_d2m_k"] - 273.15, 2)
    if "u10" in var_map:
        df["era5_u10_m_s"] = df[var_map["u10"]]
    if "v10" in var_map:
        df["era5_v10_m_s"] = df[var_map["v10"]]

    # Wind Speed & Direction
    if "u10" in var_map and "v10" in var_map:
        u = df["era5_u10_m_s"].values
        v = df["era5_v10_m_s"].values
        df["Wind_Speed_m_s"] = np.round(np.sqrt(u**2 + v**2), 2)
        df["Wind_Direction_deg"] = np.round(compute_wind_direction(u, v), 1)

    # Relative Humidity
    if "Temperature_C" in df.columns and "Dewpoint_C" in df.columns:
        df["Relative_Humidity_pct"] = np.round(
            compute_relative_humidity(df["Temperature_C"].values, df["Dewpoint_C"].values), 1
        )

    # Precipitation
    if "tp" in var_map:
        df["era5_tp_m"] = df[var_map["tp"]]
        df["Precipitation_mm"] = np.round(np.maximum(0.0, df["era5_tp_m"] * 1000.0), 3)

    # Surface Pressure
    if "sp" in var_map:
        df["era5_sp_pa"] = df[var_map["sp"]]
        df["Surface_Pressure_hPa"] = np.round(df["era5_sp_pa"] / 100.0, 2)

    # Total Cloud Cover
    if "tcc" in var_map:
        df["era5_tcc_frac"] = df[var_map["tcc"]]
        df["Cloud_Cover_pct"] = np.round(np.clip(df["era5_tcc_frac"] * 100.0, 0.0, 100.0), 1)

    # Boundary Layer Height
    if "blh" in var_map:
        df["era5_blh_m"] = df[var_map["blh"]]
        df["Boundary_Layer_Height_m"] = np.round(df["era5_blh_m"], 1)

    # Surface Solar Radiation Downwards
    if "ssrd" in var_map:
        df["era5_ssrd_j_m2"] = df[var_map["ssrd"]]
        # Accumulated Joules/m2 over 1 hour -> average flux in W/m2 (J / 3600s)
        df["Solar_Radiation_W_m2"] = np.round(np.maximum(0.0, df["era5_ssrd_j_m2"] / 3600.0), 2)

    # Nearest Monitoring Station spatial metadata
    grid_points = df[["Latitude", "Longitude"]].drop_duplicates().values
    proximity_map = {}
    for lat, lon in grid_points:
        st_name, dist_km = find_nearest_station(lat, lon)
        proximity_map[(lat, lon)] = (st_name, dist_km)

    df["Nearest_Station_Name"] = df.apply(lambda r: proximity_map[(r["Latitude"], r["Longitude"])][0], axis=1)
    df["Nearest_Station_Distance_km"] = df.apply(lambda r: proximity_map[(r["Latitude"], r["Longitude"])][1], axis=1)

    # Organized Column Ordering
    id_cols = [
        "Timestamp_UTC", "Timestamp_IST", "Latitude", "Longitude",
        "Nearest_Station_Name", "Nearest_Station_Distance_km"
    ]
    derived_cols = [
        "Temperature_C", "Dewpoint_C", "Relative_Humidity_pct",
        "Wind_Speed_m_s", "Wind_Direction_deg", "Precipitation_mm",
        "Surface_Pressure_hPa", "Cloud_Cover_pct",
        "Boundary_Layer_Height_m", "Solar_Radiation_W_m2"
    ]
    raw_cols = [
        "era5_t2m_k", "era5_d2m_k", "era5_u10_m_s", "era5_v10_m_s",
        "era5_sp_pa", "era5_tp_m", "era5_tcc_frac", "era5_blh_m", "era5_ssrd_j_m2"
    ]

    all_ordered = [c for c in id_cols if c in df.columns]
    all_ordered += [c for c in derived_cols if c in df.columns]
    all_ordered += [c for c in raw_cols if c in df.columns]

    df = df[all_ordered].copy()
    df.sort_values(by=["Timestamp_UTC", "Latitude", "Longitude"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    ds.close()
    return df


def generate_weather_quality_report(df: pd.DataFrame, report_path: Path, source_files: List[str]) -> None:
    """
    Generates a comprehensive multi-sheet Excel Data Quality Report for the ERA5 weather dataset.
    """
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    font_title = Font(name="Calibri", size=15, bold=True, color="1F497D")
    font_subtitle = Font(name="Calibri", size=10, italic=True, color="595959")
    font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    font_bold = Font(name="Calibri", size=11, bold=True)
    font_regular = Font(name="Calibri", size=11)
    fill_header = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    fill_accent = PatternFill(start_color="DCE6F1", end_color="DCE6F1", fill_type="solid")
    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )

    # 1. Executive Summary
    ws1 = wb.create_sheet(title="Executive_Summary")
    ws1.views.sheetView[0].showGridLines = True
    ws1["A1"] = "BENGALURU ERA5 METEOROLOGICAL DATA QUALITY REPORT"
    ws1["A1"].font = font_title
    ws1["A2"] = "Copernicus Climate Data Store (CDS) Reanalysis Integration for PySpark Research"
    ws1["A2"].font = font_subtitle

    summary_items = [
        ("Source Dataset", "Copernicus ERA5 Reanalysis (reanalysis-era5-single-levels)"),
        ("Source Data Provider", "ECMWF / Copernicus Climate Change Service (C3S)"),
        ("Geographical Bounding Box", "North: 13.25, South: 12.75, West: 77.35, East: 77.85"),
        ("Grid Resolution", "0.25° x 0.25° (~27.5 km grid spacing)"),
        ("Unique Spatial Grid Nodes", f"{df[['Latitude', 'Longitude']].drop_duplicates().shape[0]} grid vertices across Bengaluru"),
        ("Temporal Resolution", "Hourly continuous observations"),
        ("Observation Period (UTC)", f"{df['Timestamp_UTC'].min()} to {df['Timestamp_UTC'].max()}"),
        ("Observation Period (IST)", f"{df['Timestamp_IST'].min()} to {df['Timestamp_IST'].max()}"),
        ("Total Meteorological Records", f"{len(df):,}"),
        ("Primary Output File (CSV)", "bengaluru_era5_weather.csv"),
        ("Primary Output File (Excel)", "bengaluru_era5_weather.xlsx"),
        ("Source NetCDF Files Processed", ", ".join(source_files)),
    ]

    ws1.cell(row=4, column=1, value="Attribute / Dimension").font = font_header
    ws1.cell(row=4, column=1).fill = fill_header
    ws1.cell(row=4, column=2, value="Value / Specification").font = font_header
    ws1.cell(row=4, column=2).fill = fill_header

    for r_idx, (k, v) in enumerate(summary_items, start=5):
        c1 = ws1.cell(row=r_idx, column=1, value=k)
        c2 = ws1.cell(row=r_idx, column=2, value=str(v))
        c1.font = font_bold
        c2.font = font_regular
        c1.border = thin_border
        c2.border = thin_border
        if r_idx % 2 == 0:
            c1.fill = fill_accent
            c2.fill = fill_accent

    # 2. Variable Dictionary & Unit Conversions
    ws2 = wb.create_sheet(title="Variable_Data_Dictionary")
    ws2.views.sheetView[0].showGridLines = True

    var_info_list = [
        ("Timestamp_UTC", "Temporal", "UTC", "YYYY-MM-DD HH:MM:SS", "Official ECMWF standard UTC observation timestamp"),
        ("Timestamp_IST", "Temporal", "IST (UTC+5:30)", "YYYY-MM-DD HH:MM:SS", "Indian Standard Time for alignment with local air quality sensors"),
        ("Latitude", "Spatial", "Degrees North", "Float", "ERA5 grid node latitude"),
        ("Longitude", "Spatial", "Degrees East", "Float", "ERA5 grid node longitude"),
        ("Nearest_Station_Name", "Spatial", "Text", "String", "Closest Bengaluru air-quality monitoring station"),
        ("Nearest_Station_Distance_km", "Spatial", "km", "Float", "Haversine distance to nearest monitoring station"),
        ("Temperature_C", "Standardized", "°C", "Float", "2m Ambient Temperature converted from Kelvin: T(K) - 273.15"),
        ("Dewpoint_C", "Standardized", "°C", "Float", "2m Dewpoint Temperature converted from Kelvin: Td(K) - 273.15"),
        ("Relative_Humidity_pct", "Derived", "%", "Float", "Relative Humidity derived via August-Roche-Magnus formula (0-100%)"),
        ("Wind_Speed_m_s", "Derived", "m/s", "Float", "10m Horizontal Wind Speed: sqrt(u10^2 + v10^2)"),
        ("Wind_Direction_deg", "Derived", "Degrees", "Float", "Meteorological wind direction FROM which wind blows (0-360°)"),
        ("Precipitation_mm", "Standardized", "mm", "Float", "Total precipitation converted from metres: tp * 1000"),
        ("Surface_Pressure_hPa", "Standardized", "hPa", "Float", "Surface atmospheric pressure converted from Pascals: sp / 100"),
        ("Cloud_Cover_pct", "Standardized", "%", "Float", "Total Cloud Cover converted from fraction: tcc * 100"),
        ("Boundary_Layer_Height_m", "Standardized", "m", "Float", "Planetary boundary layer height (BLH)"),
        ("Solar_Radiation_W_m2", "Derived", "W/m²", "Float", "Surface solar radiation downwards converted from J/m²: ssrd / 3600"),
        ("era5_t2m_k", "Raw ERA5", "Kelvin", "Float", "Original ECMWF 2m Temperature"),
        ("era5_d2m_k", "Raw ERA5", "Kelvin", "Float", "Original ECMWF 2m Dewpoint Temperature"),
        ("era5_u10_m_s", "Raw ERA5", "m/s", "Float", "Original ECMWF 10m U-component of wind"),
        ("era5_v10_m_s", "Raw ERA5", "m/s", "Float", "Original ECMWF 10m V-component of wind"),
        ("era5_sp_pa", "Raw ERA5", "Pa", "Float", "Original ECMWF Surface Pressure"),
        ("era5_tp_m", "Raw ERA5", "m", "Float", "Original ECMWF Total Precipitation accumulated"),
        ("era5_tcc_frac", "Raw ERA5", "0-1", "Float", "Original ECMWF Total Cloud Cover fraction"),
        ("era5_blh_m", "Raw ERA5", "m", "Float", "Original ECMWF Boundary Layer Height"),
        ("era5_ssrd_j_m2", "Raw ERA5", "J/m²", "Float", "Original ECMWF Surface Solar Radiation Downwards accumulated"),
    ]

    ws2_headers = ["Variable Name", "Category", "Measurement Unit", "Format / Type", "Description & Scientific Formula"]
    for c_idx, h in enumerate(ws2_headers, start=1):
        cell = ws2.cell(row=1, column=c_idx, value=h)
        cell.font = font_header
        cell.fill = fill_header

    for r_idx, item in enumerate(var_info_list, start=2):
        for c_idx, val in enumerate(item, start=1):
            c = ws2.cell(row=r_idx, column=c_idx, value=val)
            c.font = font_regular
            c.border = thin_border

    # 3. Descriptive Statistics
    ws3 = wb.create_sheet(title="Descriptive_Statistics")
    ws3.views.sheetView[0].showGridLines = True

    stat_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c not in ["Latitude", "Longitude"]]
    ws3_headers = ["Variable", "Unit", "Count", "Mean", "Std Dev", "Min", "25%", "Median (50%)", "75%", "Max"]
    for c_idx, h in enumerate(ws3_headers, start=1):
        cell = ws3.cell(row=1, column=c_idx, value=h)
        cell.font = font_header
        cell.fill = fill_header

    for r_idx, col in enumerate(stat_cols, start=2):
        desc = df[col].describe()
        unit_str = next((item[2] for item in var_info_list if item[0] == col), "N/A")
        row_vals = [
            col,
            unit_str,
            int(desc["count"]),
            round(float(desc["mean"]), 2),
            round(float(desc["std"]), 2),
            round(float(desc["min"]), 2),
            round(float(desc["25%"]), 2),
            round(float(desc["50%"]), 2),
            round(float(desc["75%"]), 2),
            round(float(desc["max"]), 2),
        ]
        for c_idx, val in enumerate(row_vals, start=1):
            c = ws3.cell(row=r_idx, column=c_idx, value=val)
            c.font = font_regular
            c.border = thin_border

    # Adjust widths
    for ws in [ws1, ws2, ws3]:
        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            ws.column_dimensions[get_column_letter(col[0].column)].width = max(max_len + 3, 14)

    wb.save(report_path)


def export_weather_data(df: pd.DataFrame) -> None:
    """
    Exports processed weather DataFrame to CSV and Excel with memory efficiency.
    """
    csv_path = OUTPUT_DIR / "bengaluru_era5_weather.csv"
    excel_path = OUTPUT_DIR / "bengaluru_era5_weather.xlsx"

    logger.info("Exporting weather CSV: %s (%d rows)...", csv_path, len(df))
    t0 = time.time()
    df.to_csv(csv_path, index=False, encoding="utf-8")
    logger.info("CSV export completed in %.2fs (%s bytes)", time.time() - t0, f"{csv_path.stat().st_size:,}")

    logger.info("Exporting weather Excel: %s...", excel_path)
    t1 = time.time()
    wb = Workbook(write_only=True)
    ws = wb.create_sheet(title="ERA5_Weather_Bengaluru")
    ws.append(list(df.columns))

    chunk_size = 50000
    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i : i + chunk_size]
        for row in chunk.itertuples(index=False, name=None):
            clean_row = [None if (isinstance(val, float) and pd.isna(val)) else val for val in row]
            ws.append(clean_row)

    wb.save(excel_path)
    logger.info("Excel export completed in %.2fs (%s bytes)", time.time() - t1, f"{excel_path.stat().st_size:,}")


def main():
    logger.info("=" * 80)
    logger.info("Bengaluru ERA5 Meteorological Data Processing Pipeline")
    logger.info("=" * 80)

    # Search for NetCDF files in raw_weather_data
    nc_files = list(RAW_WEATHER_DIR.glob("*.nc")) + list(RAW_WEATHER_DIR.glob("*.grib"))

    if not nc_files:
        logger.warning(
            "No NetCDF (*.nc) or GRIB (*.grib) files found in %s.\n"
            "Please run 'python download_era5.py' after configuring your CDS API key\n"
            "or place downloaded ERA5 NetCDF files into 'raw_weather_data/'.",
            RAW_WEATHER_DIR
        )
        return

    dfs = []
    source_names = []
    for f in nc_files:
        logger.info("Processing source file: %s", f.name)
        df_processed = process_era5_dataset(f)
        dfs.append(df_processed)
        source_names.append(f.name)

        # Export individual processed file to processed_weather_data/
        proc_csv = PROCESSED_WEATHER_DIR / f"{f.stem}_processed.csv"
        df_processed.to_csv(proc_csv, index=False, encoding="utf-8")
        logger.info("Saved processed grid data to: %s", proc_csv.name)

    # Combine all processed weather datasets
    master_weather = pd.concat(dfs, ignore_index=True)
    master_weather.drop_duplicates(subset=["Timestamp_UTC", "Latitude", "Longitude"], keep="first", inplace=True)
    master_weather.sort_values(by=["Timestamp_UTC", "Latitude", "Longitude"], inplace=True)
    master_weather.reset_index(drop=True, inplace=True)

    # Export master files
    export_weather_data(master_weather)

    # Generate Data Quality Report
    report_path = OUTPUT_DIR / "weather_data_quality_report.xlsx"
    generate_weather_quality_report(master_weather, report_path, source_names)

    logger.info("[SUCCESS] ERA5 Meteorological Data Processing & Quality Audit Complete!")


if __name__ == "__main__":
    main()
