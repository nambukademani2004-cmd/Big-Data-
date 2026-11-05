# Bengaluru Air Pollution Dataset Collection and Integration

**Research Project:**  
*A PySpark-Based Big Data Analysis of Air Pollution and Meteorological Patterns in Bengaluru*

---

## 1. Overview & Research Context

This project provides an automated, robust, and reproducible Python data engineering pipeline that downloads, audits, standardizes, filters, and integrates continuous air quality monitoring datasets from all **13 monitoring locations** across the city of Bengaluru, Karnataka, India.

The source datasets are published on the OpenCity / Karnataka State Pollution Control Board (KSPCB) / Central Pollution Control Board (CPCB) open data portal. Each station records continuous observation readings at a high temporal resolution of **15-minute intervals** spanning **2024 through 2025**.

The output of this pipeline is a unified, authentic, clean Big Data dataset containing **866,044 observations**, perfectly conditioned for merging with ERA5 meteorological reanalysis data and high-performance processing in **Apache Spark / PySpark**.

---

## 2. Monitoring Locations Processed

All 13 official monitoring stations specified in the study were queried, validated, and downloaded:

| # | Station Name | Station ID | Authority | Raw Records | Retained Records |
|---|---|---|---|---|---|
| 1 | **Bapuji Nagar** | `site_1553` | KSPCB | 64,195 | 64,194 |
| 2 | **BTM Layout** | `site_162` | CPCB | 63,845 | 63,844 |
| 3 | **City Railway Station** | `site_165` | KSPCB | 51,173 | 51,172 |
| 4 | **Hebbal** | `site_1554` | KSPCB | 67,961 | 67,960 |
| 5 | **Hombegowda Nagar** | `site_1555` | KSPCB | 69,167 | 69,166 |
| 6 | **Jayanagar 5th Block** | `site_1556` | KSPCB | 66,786 | 66,785 |
| 7 | **Jigani** | `site_5729` | KSPCB | 70,177 | 70,176 |
| 8 | **Kasturi Nagar** | `site_5681` | KSPCB | 70,177 | 70,176 |
| 9 | **Peenya** | `site_163` | CPCB | 65,456 | 65,455 |
| 10 | **RVCE Mailasandra** | `site_5678` | KSPCB | 70,177 | 70,176 |
| 11 | **Sanegurava Halli** | `site_166` | KSPCB | 66,589 | 66,588 |
| 12 | **Shivapura Peenya** | `site_5686` | KSPCB | 70,177 | 70,176 |
| 13 | **Silk Board** | `site_1558` | KSPCB | 70,177 | 70,176 |
| **TOTAL** | — | — | — | **866,057** | **866,044** |

*(Note: In each raw dataset, exactly 1 non-observation artifact row containing only the annual boundary marker `'2025'` was sanitized, leaving 866,044 authentic continuous observations with 0 duplicates).*

---

## 3. Strict Column Selection & Removal Logic (Rule 4)

In accordance with strict Big Data comparative methodology:
> **The final integrated dataset contains ONLY columns that exist in every station AND have actual non-null, non-empty values in EVERY location's dataset.**

### A. Removed Columns (20 Columns)
The following 20 parameters were eliminated across all stations because they were completely empty (0 valid readings) or unavailable in at least one monitoring location:
- **`PM2.5`**: 100% missing in *City Railway Station* and *Sanegurava Halli*.
- **`NH3`**: 100% missing in *City Railway Station* and *Sanegurava Halli*.
- **`Ozone`**: 100% missing in *City Railway Station* and *Sanegurava Halli*.
- **`Benzene`**: 100% missing in *City Railway Station* and *Sanegurava Halli*.
- **`NO`**: 100% missing in *Hebbal*.
- **`NOx`**: 100% missing in *Hebbal*.
- **`AT` (Ambient Temperature)**: 100% missing in *BTM Layout*, *City Railway Station*, and *Peenya*.
- **`RH` (Relative Humidity)**: 100% missing in *City Railway Station*.
- **`WS` (Wind Speed)**: 100% missing in *City Railway Station*, *Hombegowda Nagar*, *Jayanagar 5th Block*, and *Peenya*.
- **`WD` (Wind Direction)**: 100% missing in *City Railway Station* and *Peenya*.
- **`Toluene`**: 100% missing in *City Railway Station*, *Hebbal*, *Sanegurava Halli*, and *Shivapura Peenya*.
- **`BP` (Barometric Pressure)**: 100% missing in *City Railway Station*, *Hebbal*, and *Sanegurava Halli*.
- **`SR` (Solar Radiation)**: 100% missing in 7 stations.
- **`RF` & `TOT_RF` (Rainfall)**: 100% missing in 8–9 stations.
- **`Eth_Benzene` & `MP_Xylene`**: 100% missing in 8–9 stations.
- **`VWS` (Vertical Wind Speed)**: 100% missing in 12 stations.
- **`Xylene` & `O_Xylene`**: 100% missing in all 13 stations.

### B. Retained Final Columns (9 Columns)
The following 9 standardized parameters have authentic, non-null values across **all 13 stations**:
1. **`Station_Name`** *(String)*: Standardized monitoring location name.
2. **`Station_ID`** *(String)*: Unique CPCB/KSPCB station identifier (e.g., `site_1553`).
3. **`City`** *(String)*: Bengaluru.
4. **`State`** *(String)*: Karnataka.
5. **`Timestamp`** *(String/Timestamp)*: Standardized observation timestamp (`YYYY-MM-DD HH:MM:SS`) preserving the 15-minute frequency.
6. **`PM10`** *(Float)*: Particulate Matter $\le 10\ \mu\text{m}$ in $\mu\text{g/m}^3$ (767,579 valid readings across all stations).
7. **`NO2`** *(Float)*: Nitrogen Dioxide in $\mu\text{g/m}^3$ (780,026 valid readings across all stations).
8. **`SO2`** *(Float)*: Sulfur Dioxide in $\mu\text{g/m}^3$ (783,235 valid readings across all stations).
9. **`CO`** *(Float)*: Carbon Monoxide in $\text{mg/m}^3$ (759,157 valid readings across all stations).

> **Important Data Authenticity Rule:** Missing values on individual rows are strictly preserved as true missing values (`NaN`/`None`). No values are artificially fabricated, estimated, or filled with zeros.

---

## 4. Project Directory Structure

```text
bengaluru_air_quality_project/
│
├── main.py                    # Complete end-to-end Python pipeline
├── requirements.txt           # Python dependencies
├── README.md                  # Detailed documentation and research guide
│
├── raw_data/                  # Preserved authentic original CSV files
│   ├── Bapuji_Nagar.csv
│   ├── BTM_Layout.csv
│   ├── City_Railway_Station.csv
│   ├── Hebbal.csv
│   ├── Hombegowda_Nagar.csv
│   ├── Jayanagar_5th_Block.csv
│   ├── Jigani.csv
│   ├── Kasturi_Nagar.csv
│   ├── Peenya.csv
│   ├── RVCE_Mailasandra.csv
│   ├── Sanegurava_Halli.csv
│   ├── Shivapura_Peenya.csv
│   └── Silk_Board.csv
│
└── output/                    # Final integrated datasets
    ├── bengaluru_integrated_air_quality_2024_2025.csv   # 866,044 rows, 9 cols (72.2 MB)
    └── bengaluru_integrated_air_quality_2024_2025.xlsx  # Sheet: 'Integrated_Air_Quality' (36.3 MB)
```

---

## 5. How to Run in Visual Studio Code (Step-by-Step)

### Step 1: Open Project in VS Code
1. Launch **Visual Studio Code**.
2. Go to **File** $\rightarrow$ **Open Folder...**
3. Select the folder:
   ```text
   C:\Users\nambu\OneDrive\Desktop\BIG_DATA_POSTER\bengaluru_air_quality_project
   ```

### Step 2: Select Python Interpreter
1. Press `Ctrl + Shift + P` to open the Command Palette.
2. Type `Python: Select Interpreter` and hit Enter.
3. Choose your Python 3.11 environment (e.g. `C:\Users\nambu\AppData\Local\Python\bin\python.exe` or standard `python.exe`).

### Step 3: Open Terminal in VS Code
1. Open a new terminal by pressing `Ctrl + ~` (or **Terminal** $\rightarrow$ **New Terminal**).
2. Install the required dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

### Step 4: Run the Script
Execute `main.py` directly from the terminal:
```powershell
python main.py
```
*(Or right-click anywhere in `main.py` in the editor and click **Run Python File in Terminal**).*

---

## 6. Functional Architecture of `main.py`

The script is cleanly partitioned into modular, reusable functions:
1. `download_dataset(station_key, station_meta, target_dir)`: Connects to OpenCity CKAN API, retrieves direct CSV URLs, and streams downloads with HTTP retry handling. Skips re-downloading if already present.
2. `inspect_dataset(file_path)`: Loads raw CSVs, extracts row counts, and catalogs raw column names.
3. `standardize_columns(df, station_key, station_display_name)`: Maps column variations into consistent, PySpark-compatible names and adds the `Station_Name` column.
4. `identify_common_valid_columns(standardized_dfs)`: Evaluates intersection and column completeness across all 13 stations, identifying columns to retain vs. drop.
5. `clean_dataset(df, target_columns, station_display_name)`: Filters target columns, removes annual separator lines, standardizes timestamps (`YYYY-MM-DD HH:MM:SS`), coerces numeric data types, and eliminates duplicates.
6. `combine_datasets(cleaned_dfs, column_order)`: Combines all station dataframes vertically into a unified dataframe and sorts chronologically.
7. `validate_integrated_dataset(...)`: Computes and displays the comprehensive research audit report.
8. `export_final_dataset(integrated_df, output_csv, output_excel, sheet_name)`: Exports CSV and uses `openpyxl`'s memory-optimized `write_only` streaming mode to export the 866,044-row Excel workbook with sheet `Integrated_Air_Quality`.

---

## 7. PySpark Integration Guide for Poster Presentation

When ready to combine this dataset with ERA5 meteorological reanalysis data in PySpark:

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("BengaluruAirPollutionAnalysis") \
    .config("spark.driver.memory", "4g") \
    .getOrCreate()

# Load integrated air quality dataset
aq_df = spark.read.csv(
    "output/bengaluru_integrated_air_quality_2024_2025.csv",
    header=True,
    inferSchema=True
)

# Parse timestamp into Spark TimestampType
aq_df = aq_df.withColumn("Timestamp", to_timestamp(col("Timestamp"), "yyyy-MM-dd HH:mm:ss"))

# Summary of records
aq_df.printSchema()
print(f"Total Observations: {aq_df.count():,}")

# Ready to join with ERA5 weather data on Timestamp and Station coordinates!
```
