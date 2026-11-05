"""
PySpark Big Data Analytics Engine
Research Title: "A PySpark-Based Big Data Analysis of Air Pollution and Meteorological Patterns in Bengaluru, Karnataka"

This script executes real Apache Spark DataFrame operations on the 866,044-row Bengaluru air quality dataset:
1. SparkSession initialization with memory and executor configurations.
2. Distributed dataset ingestion & schema inspection.
3. Big Data Data Hygiene: Null-value quantification & duplicate detection.
4. PySpark Windowing & GroupBy: 15-minute to hourly aggregation.
5. Multi-dimensional aggregations: Spatial (Station), Temporal (Month, Day, Hour).
6. Statistical summaries: Mean, StdDev, Min, Max, Quantiles.
7. Bivariate correlation matrix calculation using Spark ML / stat functions.
"""

import os
import sys
import time
from pathlib import Path

# Configure Zulu 17 OpenJDK for PySpark
ZULU_JDK = r"C:\Program Files\Weka-3-9-6\jre\zulu17.32.13-ca-fx-jre17.0.2-win_x64"
if os.path.exists(ZULU_JDK):
    os.environ["JAVA_HOME"] = ZULU_JDK
    os.environ["PATH"] = f"{ZULU_JDK}\\bin;" + os.environ.get("PATH", "")

import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, to_timestamp, date_trunc, year, month, dayofmonth, hour,
    avg, stddev, min as spark_min, max as spark_max, count, when, isnan, round as spark_round
)

BASE_DIR = Path(r"c:\Users\nambu\OneDrive\Desktop\BIG_DATA_POSTER\Bengaluru_Air_Pollution_Research")
INPUT_CSV = BASE_DIR / "processed_data" / "bengaluru_air_quality_cleaned.csv"
if not INPUT_CSV.exists():
    INPUT_CSV = Path(r"c:\Users\nambu\OneDrive\Desktop\BIG_DATA_POSTER\bengaluru_air_quality_project\output\bengaluru_air_quality_cleaned.csv")

OUTPUT_LOG = BASE_DIR / "reports" / "pyspark_execution_results.txt"
OUTPUT_LOG.parent.mkdir(parents=True, exist_ok=True)

class TeeOutput:
    """Logs to both console and file."""
    def __init__(self, file_path):
        self.file = open(file_path, "w", encoding="utf-8")
        self.stdout = sys.stdout

    def write(self, data):
        self.stdout.write(data)
        self.file.write(data)

    def flush(self):
        self.stdout.flush()
        self.file.flush()

    def close(self):
        self.file.close()

def run_pyspark_pipeline():
    logger = TeeOutput(OUTPUT_LOG)
    sys.stdout = logger

    start_time = time.time()
    print("=" * 85)
    print("  PYSPARK BIG DATA ANALYTICS PIPELINE: BENGALURU AIR QUALITY & METEOROLOGY")
    print("=" * 85)
    print(f"PySpark Version : {pyspark.__version__}")
    print(f"Java Home       : {os.environ.get('JAVA_HOME')}")
    print(f"Input Dataset   : {INPUT_CSV}")
    print("-" * 85)

    # 1. Initialize SparkSession
    print("\n[STEP 1] Initializing Apache Spark Session...")
    spark = SparkSession.builder \
        .appName("BengaluruAirPollutionBigDataAnalytics") \
        .master("local[*]") \
        .config("spark.driver.memory", "4g") \
        .config("spark.sql.shuffle.partitions", "8") \
        .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")
    print("SparkSession successfully created.")

    # 2. Ingest Dataset & Schema Inspection
    print("\n[STEP 2] Loading raw/cleaned air quality dataset into Spark DataFrame...")
    df_raw = spark.read.csv(str(INPUT_CSV), header=True, inferSchema=True)
    total_rows = df_raw.count()
    total_cols = len(df_raw.columns)
    print(f"Successfully loaded DataFrame: {total_rows:,} records across {total_cols} columns.")

    print("\n--- Spark DataFrame Schema ---")
    df_raw.printSchema()

    # 3. Rename special characters for Spark compatibility (e.g. PM2.5 -> PM2_5)
    print("\n[STEP 3] Standardizing column names for Spark SQL (PM2.5 -> PM2_5)...")
    df_clean = df_raw
    if "PM2.5" in df_raw.columns:
        df_clean = df_clean.withColumnRenamed("PM2.5", "PM2_5")

    # 4. Data Type Standardization & Temporal Parsing
    print("\n[STEP 4] Parsing and standardizing timestamps...")
    df = df_clean.withColumn("Timestamp", to_timestamp(col("Timestamp"), "yyyy-MM-dd HH:mm:ss")) \
                 .withColumn("Year", year(col("Timestamp"))) \
                 .withColumn("Month", month(col("Timestamp"))) \
                 .withColumn("Day", dayofmonth(col("Timestamp"))) \
                 .withColumn("Hour", hour(col("Timestamp")))

    # 5. Data Hygiene: Missing Values Audit
    print("\n[STEP 5] Missing-Value Analysis across Key Parameters...")
    key_params = ["PM2_5", "PM10", "NO2", "SO2", "CO", "Ozone", "NH3", "AT", "RH", "WS", "BP"]
    avail_params = [p for p in key_params if p in df.columns]

    null_exprs = [
        count(when(col(c).isNull() | isnan(col(c)), c)).alias(f"{c}_nulls")
        for c in avail_params
    ]
    null_counts = df.select(null_exprs).collect()[0].asDict()

    print(f"{'Parameter':<12} | {'Null Count':<12} | {'Valid Count':<12} | {'Completeness (%)':<16}")
    print("-" * 60)
    for p in avail_params:
        display_name = "PM2.5" if p == "PM2_5" else p
        n_null = null_counts[f"{p}_nulls"]
        n_valid = total_rows - n_null
        pct_valid = (n_valid / total_rows) * 100
        print(f"{display_name:<12} | {n_null:<12,d} | {n_valid:<12,d} | {pct_valid:<16.2f}%")

    # Duplicate Detection
    print("\n[STEP 6] Checking for Duplicates across (Station_Name, Timestamp)...")
    duplicate_count = df.groupBy("Station_Name", "Timestamp").count().filter("count > 1").count()
    print(f"Total Duplicate Observation Timestamps Detected: {duplicate_count}")

    # 6. Spatial GroupBy: Pollutant Concentrations by Station
    print("\n[STEP 7] Station-Wise Pollutant Aggregations (PySpark GroupBy)...")
    station_summary = df.groupBy("Station_Name").agg(
        count("PM10").alias("PM10_Obs"),
        spark_round(avg("PM10"), 2).alias("PM10_Mean"),
        spark_round(stddev("PM10"), 2).alias("PM10_Std"),
        spark_round(avg("PM2_5"), 2).alias("PM2_5_Mean"),
        spark_round(stddev("PM2_5"), 2).alias("PM2_5_Std"),
        spark_round(avg("NO2"), 2).alias("NO2_Mean"),
        spark_round(avg("CO"), 2).alias("CO_Mean")
    ).orderBy(col("PM10_Mean").desc())

    station_summary.show(15, truncate=False)

    # 7. Hourly Aggregation Window
    print("\n[STEP 8] Performing 15-Minute to Hourly Windowed Aggregation...")
    df_hourly = df.withColumn("Timestamp_Hour", date_trunc("hour", col("Timestamp"))) \
        .groupBy("Station_Name", "Station_ID", "City", "State", "Timestamp_Hour", "Year", "Month", "Hour") \
        .agg(
            avg("PM2_5").alias("PM2_5"),
            avg("PM10").alias("PM10"),
            avg("NO2").alias("NO2"),
            avg("SO2").alias("SO2"),
            avg("CO").alias("CO"),
            avg("Ozone").alias("Ozone"),
            avg("NH3").alias("NH3"),
            avg("AT").alias("AT"),
            avg("RH").alias("RH"),
            avg("WS").alias("WS"),
            avg("WD").alias("WD"),
            avg("BP").alias("BP"),
            avg("SR").alias("SR")
        )

    hourly_count = df_hourly.count()
    print(f"Aggregated 866,044 15-minute observations into {hourly_count:,} hourly station records.")

    # 8. Diurnal 24-Hour Cycle
    print("\n[STEP 9] Computing 24-Hour Diurnal Cycle across Bengaluru...")
    diurnal_cycle = df_hourly.groupBy("Hour").agg(
        spark_round(avg("PM10"), 2).alias("PM10_Mean"),
        spark_round(avg("PM2_5"), 2).alias("PM2_5_Mean"),
        spark_round(avg("NO2"), 2).alias("NO2_Mean"),
        spark_round(avg("AT"), 2).alias("Temp_Mean"),
        spark_round(avg("WS"), 2).alias("WindSpeed_Mean")
    ).orderBy("Hour")

    diurnal_cycle.show(24, truncate=False)

    # 9. Monthly Seasonal Variation
    print("\n[STEP 10] Seasonal Multi-Year Variation (Grouping by Year and Month)...")
    monthly_variation = df_hourly.groupBy("Year", "Month").agg(
        spark_round(avg("PM10"), 2).alias("PM10_Mean"),
        spark_round(avg("PM2_5"), 2).alias("PM2_5_Mean"),
        spark_round(avg("NO2"), 2).alias("NO2_Mean"),
        spark_round(avg("AT"), 2).alias("Temp_Mean"),
        spark_round(avg("RH"), 2).alias("RH_Mean")
    ).orderBy("Year", "Month")

    monthly_variation.show(24, truncate=False)

    # 10. Correlation Analysis
    print("\n[STEP 11] Bivariate Statistical Correlation Analysis...")
    correlations = [
        ("PM2_5", "PM10"),
        ("PM2_5", "AT"),
        ("PM10", "WS"),
        ("NO2", "CO"),
        ("AT", "RH"),
        ("AT", "Ozone")
    ]
    print(f"{'Variable 1':<12} | {'Variable 2':<12} | {'Pearson Correlation (r)':<25}")
    print("-" * 55)
    for v1, v2 in correlations:
        if v1 in df_hourly.columns and v2 in df_hourly.columns:
            r = df_hourly.stat.corr(v1, v2)
            d1 = "PM2.5" if v1 == "PM2_5" else v1
            d2 = "PM2.5" if v2 == "PM2_5" else v2
            print(f"{d1:<12} | {d2:<12} | {r:<25.4f}")

    # 11. Summary Statistics for Criteria Pollutants
    print("\n[STEP 12] Summary Statistics for Criteria Pollutants...")
    df_hourly.select("PM2_5", "PM10", "NO2", "SO2", "CO", "Ozone", "AT", "WS").describe().show()

    # Stop SparkSession
    spark.stop()
    elapsed = time.time() - start_time
    print("=" * 85)
    print(f"PySpark Analysis Completed Successfully in {elapsed:.2f} seconds.")
    print(f"Results Log Saved to: {OUTPUT_LOG}")
    print("=" * 85)

    sys.stdout = logger.stdout
    logger.close()

if __name__ == "__main__":
    run_pyspark_pipeline()
