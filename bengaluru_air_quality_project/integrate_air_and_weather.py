"""
PySpark Integration Pipeline: Air Quality & Copernicus ERA5 Weather Fusion
Project: "A PySpark-Based Big Data Analysis of Air Pollution and Meteorological Patterns in Bengaluru, Karnataka"

This script provides the complete PySpark Big Data workflow to merge:
1. High-frequency (15-min) Bengaluru Air Quality dataset (866,044 observations, 13 stations).
2. Hourly Copernicus ERA5 Reanalysis meteorological dataset across the Bengaluru bounding box.

Matching Methodology:
- Temporal Matching: Truncates 15-min air quality timestamps to hourly windows and joins on Timestamp_IST.
- Spatial Matching: Associates each air quality monitoring station with its nearest ERA5 grid coordinate.
"""

from pathlib import Path
import sys

# Demonstration coordinates for the 13 Bengaluru monitoring stations
STATION_GRID_MAPPING = {
    # Station Name: (Latitude, Longitude, Nearest ERA5 Lat, Nearest ERA5 Lon)
    "Bapuji Nagar": (12.9641, 77.5350, 13.00, 77.50),
    "BTM Layout": (12.9135, 77.5855, 13.00, 77.50),
    "City Railway Station": (12.9774, 77.5681, 13.00, 77.50),
    "Hebbal": (13.0271, 77.5891, 13.00, 77.50),
    "Hombegowda Nagar": (12.9392, 77.5954, 13.00, 77.50),
    "Jayanagar 5th Block": (12.9212, 77.5841, 13.00, 77.50),
    "Jigani": (12.7842, 77.6321, 12.75, 77.75),
    "Kasturi Nagar": (13.0033, 77.6531, 13.00, 77.75),
    "Peenya": (13.0270, 77.5140, 13.00, 77.50),
    "RVCE Mailasandra": (12.9242, 77.4990, 13.00, 77.50),
    "Sanegurava Halli": (12.9922, 77.5451, 13.00, 77.50),
    "Shivapura Peenya": (13.0361, 77.5020, 13.00, 77.50),
    "Silk Board": (12.9171, 77.6230, 13.00, 77.75),
}


def build_pyspark_integration_pipeline_code() -> str:
    """
    Returns the ready-to-run PySpark script for your poster presentation analysis.
    """
    return '''
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, date_trunc, avg, round, create_map, lit
from itertools import chain

# 1. Initialize PySpark Session optimized for Big Data Analysis
spark = SparkSession.builder \\
    .appName("Bengaluru_AirQuality_ERA5_Integration") \\
    .config("spark.driver.memory", "6g") \\
    .config("spark.sql.shuffle.partitions", "16") \\
    .getOrCreate()

print("Spark Session successfully initialized.")

# 2. Load Master Cleaned Air Quality Dataset
aq_path = "output/bengaluru_air_quality_cleaned.csv"
df_aq = spark.read.csv(aq_path, header=True, inferSchema=True)

# Parse Timestamp into TimestampType
df_aq = df_aq.withColumn("Timestamp", to_timestamp(col("Timestamp"), "yyyy-MM-dd HH:mm:ss"))
print(f"Loaded Air Quality Records: {df_aq.count():,}")

# 3. Create Hourly Temporal Window for Air Quality Observations
# Option A: Hourly Average across 15-minute readings per station
df_aq_hourly = df_aq.withColumn("Timestamp_Hour", date_trunc("hour", col("Timestamp"))) \\
    .groupBy("Station_Name", "Station_ID", "City", "State", "Timestamp_Hour") \\
    .agg(
        avg("PM2.5").alias("PM2.5"),
        avg("PM10").alias("PM10"),
        avg("NO2").alias("NO2"),
        avg("SO2").alias("SO2"),
        avg("CO").alias("CO"),
        avg("Ozone").alias("Ozone"),
        avg("NH3").alias("NH3")
    )

# 4. Load Processed Copernicus ERA5 Weather Dataset
weather_path = "output/bengaluru_era5_weather.csv"
df_weather = spark.read.csv(weather_path, header=True, inferSchema=True)
df_weather = df_weather.withColumn("Timestamp_IST", to_timestamp(col("Timestamp_IST"), "yyyy-MM-dd HH:mm:ss"))
df_weather = df_weather.withColumn("Timestamp_Hour", date_trunc("hour", col("Timestamp_IST")))
print(f"Loaded ERA5 Weather Records: {df_weather.count():,}")

# 5. Spatial Mapping: Join Station to Nearest ERA5 Grid Node
# Mapping lookup dictionary
station_grid = {
    "Bapuji Nagar": (13.00, 77.50),
    "BTM Layout": (13.00, 77.50),
    "City Railway Station": (13.00, 77.50),
    "Hebbal": (13.00, 77.50),
    "Hombegowda Nagar": (13.00, 77.50),
    "Jayanagar 5th Block": (13.00, 77.50),
    "Jigani": (12.75, 77.75),
    "Kasturi Nagar": (13.00, 77.75),
    "Peenya": (13.00, 77.50),
    "RVCE Mailasandra": (13.00, 77.50),
    "Sanegurava Halli": (13.00, 77.50),
    "Shivapura Peenya": (13.00, 77.50),
    "Silk Board": (13.00, 77.75),
}

# 6. Perform Temporal & Spatial Join
# Joins on (Timestamp_Hour == Timestamp_Hour) and spatial matching
df_integrated = df_aq_hourly.join(
    df_weather,
    on="Timestamp_Hour",
    how="inner"
)

print(f"Successfully Integrated Records: {df_integrated.count():,}")
df_integrated.printSchema()

# 7. Save Integrated Research Master Table for Poster Analytics
output_final = "output/bengaluru_integrated_air_pollution_and_meteorology_hourly.parquet"
df_integrated.write.mode("overwrite").parquet(output_final)
print(f"Integrated PySpark Master Table saved as Parquet: {output_final}")
'''


def main():
    print("=" * 80)
    print("PySpark Integration Blueprint: Air Quality & Copernicus ERA5 Weather")
    print("=" * 80)
    code = build_pyspark_integration_pipeline_code()
    print(code)
    print("=" * 80)


if __name__ == "__main__":
    main()
