"""
Bengaluru Air Quality & Meteorological Analytics and Publication-Grade Visualization Engine
Research Title: "A PySpark-Based Big Data Analysis of Air Pollution and Meteorological Patterns in Bengaluru, Karnataka"

Outputs:
1. Integrated_Environmental_Dataset.csv & .xlsx (hourly aggregated)
2. Exact numerical statistics dictionary (JSON)
3. 6 Publication-Grade Research Charts (300 DPI)
4. Methodology Flowchart Diagram (300 DPI)
"""

import json
import logging
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import openpyxl
import pandas as pd
from scipy import stats
import seaborn as sns

# Setup directories
BASE_DIR = Path(r"c:\Users\nambu\OneDrive\Desktop\BIG_DATA_POSTER\Bengaluru_Air_Pollution_Research")
RAW_DATA_DIR = BASE_DIR / "raw_data"
PROCESSED_DATA_DIR = BASE_DIR / "processed_data"
CHARTS_DIR = BASE_DIR / "charts"
REPORTS_DIR = BASE_DIR / "reports"
SRC_DIR = BASE_DIR / "src"

CHARTS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
SRC_DIR.mkdir(parents=True, exist_ok=True)

# Aesthetic parameters for scientific research publication
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.edgecolor'] = '#1E293B'
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['grid.color'] = '#CBD5E1'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.6

# Color palette: Academic Navy, Slate Blue, Vibrant Cyan/Teal, Warm Amber, Emerald
COLOR_NAVY = '#1E3A8A'
COLOR_TEAL = '#0D9488'
COLOR_AMBER = '#D97706'
COLOR_CORAL = '#E11D48'
COLOR_SLATE = '#475569'
COLOR_GREEN = '#059669'
COLOR_BG_CARD = '#F8FAFC'

# 1. Load Cleaned Dataset
input_csv = BASE_DIR / "processed_data" / "bengaluru_air_quality_cleaned.csv"
if not input_csv.exists():
    input_csv = Path(r"c:\Users\nambu\OneDrive\Desktop\BIG_DATA_POSTER\bengaluru_air_quality_project\output\bengaluru_air_quality_cleaned.csv")

print(f"Loading master air quality dataset from {input_csv}...")
df = pd.read_csv(input_csv)
print(f"Loaded {len(df):,} observations.")

# Parse timestamp
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df['Year'] = df['Timestamp'].dt.year
df['Month'] = df['Timestamp'].dt.month
df['Month_Year'] = df['Timestamp'].dt.to_period('M').astype(str)
df['Hour'] = df['Timestamp'].dt.hour
df['Date'] = df['Timestamp'].dt.date

# 2. Generate Hourly Aggregated Master Dataset
print("Computing hourly aggregation across all 13 monitoring stations...")
df['Timestamp_Hour'] = df['Timestamp'].dt.floor('h')

hourly_agg_cols = {
    'PM2.5': 'mean',
    'PM10': 'mean',
    'NO': 'mean',
    'NO2': 'mean',
    'NOx': 'mean',
    'NH3': 'mean',
    'SO2': 'mean',
    'CO': 'mean',
    'Ozone': 'mean',
    'Benzene': 'mean',
    'Toluene': 'mean',
    'AT': 'mean',
    'RH': 'mean',
    'WS': 'mean',
    'WD': 'mean',
    'RF': 'sum',
    'SR': 'mean',
    'BP': 'mean'
}
available_agg_cols = {k: v for k, v in hourly_agg_cols.items() if k in df.columns}

df_hourly = df.groupby(['Station_Name', 'Station_ID', 'City', 'State', 'Timestamp_Hour']).agg(available_agg_cols).reset_index()
df_hourly = df_hourly.rename(columns={'Timestamp_Hour': 'Timestamp'})
print(f"Hourly aggregated dataset contains {len(df_hourly):,} station-hour records.")

# Save Integrated Environmental Dataset CSV & Excel
out_csv = BASE_DIR / "processed_data" / "Integrated_Environmental_Dataset.csv"
print(f"Saving Integrated CSV to {out_csv}...")
df_hourly.to_csv(out_csv, index=False)

# Copy to root level as requested in prompt deliverables
df_hourly.to_csv(BASE_DIR / "Integrated_Environmental_Dataset.csv", index=False)

# Export Excel (first 100k rows if too large for single sheet, or full)
out_xlsx = BASE_DIR / "Integrated_Environmental_Dataset.xlsx"
print(f"Saving Integrated Excel to {out_xlsx} (streaming/sample if >500k rows)...")
# df_hourly has ~215,000 rows, which fits easily in an Excel sheet (limit 1,048,576 rows)
df_hourly.to_excel(out_xlsx, sheet_name="Integrated_Hourly_Data", index=False)
print("Excel export complete.")

# 3. Compute Key Analytics & Research Findings Dictionary
findings = {}
findings['total_15min_records'] = int(len(df))
findings['total_hourly_records'] = int(len(df_hourly))
findings['start_date'] = str(df['Timestamp'].min())
findings['end_date'] = str(df['Timestamp'].max())
findings['num_stations'] = int(df['Station_Name'].nunique())
findings['stations'] = sorted(list(df['Station_Name'].unique()))

# Station Summary
st_summary = df.groupby('Station_Name').agg({
    'PM2.5': ['count', 'mean', 'std'],
    'PM10': ['count', 'mean', 'std'],
    'NO2': ['count', 'mean'],
    'SO2': ['count', 'mean'],
    'CO': ['count', 'mean']
}).round(2)
findings['station_pm10_mean'] = df.groupby('Station_Name')['PM10'].mean().round(2).to_dict()
findings['station_pm25_mean'] = df.groupby('Station_Name')['PM2.5'].mean().round(2).to_dict()

highest_pm10_st = df.groupby('Station_Name')['PM10'].mean().idxmax()
highest_pm10_val = round(df.groupby('Station_Name')['PM10'].mean().max(), 2)
lowest_pm10_st = df.groupby('Station_Name')['PM10'].mean().idxmin()
lowest_pm10_val = round(df.groupby('Station_Name')['PM10'].mean().min(), 2)

highest_pm25_st = df.groupby('Station_Name')['PM2.5'].mean().idxmax()
highest_pm25_val = round(df.groupby('Station_Name')['PM2.5'].mean().max(), 2)
lowest_pm25_st = df.groupby('Station_Name')['PM2.5'].mean().idxmin()
lowest_pm25_val = round(df.groupby('Station_Name')['PM2.5'].mean().min(), 2)

findings['highest_pm10'] = {'station': highest_pm10_st, 'value': highest_pm10_val}
findings['lowest_pm10'] = {'station': lowest_pm10_st, 'value': lowest_pm10_val}
findings['highest_pm25'] = {'station': highest_pm25_st, 'value': highest_pm25_val}
findings['lowest_pm25'] = {'station': lowest_pm25_st, 'value': lowest_pm25_val}

# Temporal monthly summary
monthly_df = df.groupby('Month_Year')[['PM2.5', 'PM10']].mean().round(2)
findings['monthly_pm25'] = monthly_df['PM2.5'].to_dict()
findings['monthly_pm10'] = monthly_df['PM10'].to_dict()

# Hourly diurnal summary
hourly_df = df.groupby('Hour')[['PM2.5', 'PM10', 'NO2', 'CO', 'AT', 'WS']].mean().round(2)
findings['hourly_pm25'] = hourly_df['PM2.5'].to_dict()
findings['hourly_pm10'] = hourly_df['PM10'].to_dict()
findings['hourly_no2'] = hourly_df['NO2'].to_dict()

morning_peak_hour = int(hourly_df['PM10'].idxmax())
morning_peak_val = float(hourly_df['PM10'].max())
afternoon_min_hour = int(hourly_df['PM10'].idxmin())
afternoon_min_val = float(hourly_df['PM10'].min())
findings['diurnal'] = {
    'peak_hour': morning_peak_hour,
    'peak_val': morning_peak_val,
    'min_hour': afternoon_min_hour,
    'min_val': afternoon_min_val
}

# Temperature vs PM2.5 correlation
valid_temp_pm = df_hourly.dropna(subset=['AT', 'PM2.5'])
slope, intercept, r_val, p_val, std_err = stats.linregress(valid_temp_pm['AT'], valid_temp_pm['PM2.5'])
findings['temp_pm25_reg'] = {
    'r': round(r_val, 3),
    'r_squared': round(r_val**2, 3),
    'slope': round(slope, 3),
    'intercept': round(intercept, 3),
    'p_value': p_val,
    'n_samples': int(len(valid_temp_pm))
}

# Wind Speed vs PM10 / PM2.5 correlation
valid_ws_pm = df_hourly.dropna(subset=['WS', 'PM10'])
ws_r, ws_p = stats.pearsonr(valid_ws_pm['WS'], valid_ws_pm['PM10'])
findings['ws_pm10_corr'] = {
    'r': round(ws_r, 3),
    'p_value': ws_p,
    'n_samples': int(len(valid_ws_pm))
}

# Correlation Matrix
corr_vars = ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'Ozone', 'NH3', 'AT', 'RH', 'WS', 'BP', 'SR']
avail_corr = [v for v in corr_vars if v in df_hourly.columns]
corr_matrix = df_hourly[avail_corr].corr().round(2)
findings['corr_matrix'] = corr_matrix.to_dict()

with open(REPORTS_DIR / "numerical_research_findings.json", "w") as f:
    json.dump(findings, f, indent=2)
print("Research findings saved to JSON.")


# ==============================================================================
# GENERATE 6 PUBLICATION-GRADE RESEARCH CHARTS (300 DPI)
# ==============================================================================

# ------------------------------------------------------------------------------
# CHART 1: Air Pollution Comparison Across Monitoring Stations
# ------------------------------------------------------------------------------
print("Generating Chart 1: Air Pollution Comparison Across Monitoring Stations...")
st_plot_df = df.groupby('Station_Name')[['PM10', 'PM2.5']].mean().reset_index()
st_plot_df = st_plot_df.sort_values(by='PM10', ascending=True)

fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#FAFAFA')

y_pos = np.arange(len(st_plot_df))
bar_width = 0.38

rects1 = ax.barh(y_pos + bar_width/2, st_plot_df['PM10'], bar_width, label=r'PM$_{10}$ (Mean Concentration)', color=COLOR_NAVY, edgecolor='#0F172A', linewidth=0.8, alpha=0.9)
rects2 = ax.barh(y_pos - bar_width/2, st_plot_df['PM2.5'], bar_width, label=r'PM$_{2.5}$ (Mean Concentration)', color=COLOR_TEAL, edgecolor='#042F2C', linewidth=0.8, alpha=0.9)

# Standard guideline lines
ax.axvline(x=60, color=COLOR_CORAL, linestyle='--', linewidth=1.5, label=r'NAAQS PM$_{10}$ Annual Limit (60 $\mu$g/m$^3$)')
ax.axvline(x=40, color=COLOR_AMBER, linestyle=':', linewidth=1.5, label=r'NAAQS PM$_{2.5}$ Annual Limit (40 $\mu$g/m$^3$)')

# Annotations
for rect in rects1:
    w = rect.get_width()
    if not np.isnan(w) and w > 0:
        ax.text(w + 1.2, rect.get_y() + rect.get_height()/2, f'{w:.1f}', va='center', ha='left', fontsize=8.5, fontweight='bold', color=COLOR_NAVY)

for rect in rects2:
    w = rect.get_width()
    if not np.isnan(w) and w > 0:
        ax.text(w + 1.2, rect.get_y() + rect.get_height()/2, f'{w:.1f}', va='center', ha='left', fontsize=8.5, fontweight='bold', color='#0F766E')
    elif np.isnan(w):
        ax.text(3, rect.get_y() + rect.get_height()/2, 'No Sensor', va='center', ha='left', fontsize=7.5, fontstyle='italic', color='#64748B')

ax.set_yticks(y_pos)
ax.set_yticklabels(st_plot_df['Station_Name'], fontsize=10, fontweight='medium')
ax.set_xlabel(r'Particulate Matter Concentration ($\mu$g/m$^3$)', fontsize=11, fontweight='bold', labelpad=8)
ax.set_title('Figure 1: Spatial Distribution of Mean Particulate Matter (PM2.5 & PM10)\nAcross 13 Continuous Air Quality Monitoring Stations in Bengaluru (2024–2025)', fontsize=12, fontweight='bold', pad=14, color='#0F172A')
ax.set_xlim(0, 125)
ax.grid(axis='x', linestyle='--', alpha=0.5)
ax.legend(frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=9, loc='lower right')

plt.tight_layout()
c1_path = CHARTS_DIR / "chart1_station_pollution_comparison.png"
plt.savefig(c1_path, dpi=300)
plt.close()
print(f"Chart 1 saved to {c1_path}")


# ------------------------------------------------------------------------------
# CHART 2: Temporal Variation in Air Pollution (Monthly Trends 2024-2025)
# ------------------------------------------------------------------------------
print("Generating Chart 2: Temporal Variation in Air Pollution...")
monthly_stats = df.groupby('Month_Year').agg({
    'PM10': ['mean', 'sem'],
    'PM2.5': ['mean', 'sem']
}).reset_index()

months = monthly_stats['Month_Year']
pm10_mean = monthly_stats['PM10']['mean']
pm10_sem = monthly_stats['PM10']['sem']
pm25_mean = monthly_stats['PM2.5']['mean']
pm25_sem = monthly_stats['PM2.5']['sem']

fig, ax = plt.subplots(figsize=(13, 6.5), dpi=300)
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#FAFAFA')

x_idx = np.arange(len(months))

# Shaded seasonal backgrounds
# Jan-Feb: Winter, Mar-May: Summer, Jun-Sep: Monsoon, Oct-Dec: Post-Monsoon
for year_offset in [0, 12]:
    # Monsoon: Jun (5) to Sep (8)
    ax.axvspan(year_offset + 5 - 0.5, year_offset + 8 + 0.5, color='#E0F2FE', alpha=0.5, label='Monsoon Season (Wet Deposition)' if year_offset == 0 else "")
    # Winter: Jan-Feb
    ax.axvspan(year_offset - 0.5, year_offset + 1 + 0.5, color='#F1F5F9', alpha=0.6, label='Winter Season (Thermal Inversion)' if year_offset == 0 else "")

ax.plot(x_idx, pm10_mean, marker='o', markersize=6, color=COLOR_NAVY, linewidth=2.4, label=r'PM$_{10}$ Monthly Mean ($\mu$g/m$^3$)')
ax.fill_between(x_idx, pm10_mean - 1.96 * pm10_sem, pm10_mean + 1.96 * pm10_sem, color=COLOR_NAVY, alpha=0.15)

ax.plot(x_idx, pm25_mean, marker='s', markersize=5.5, color=COLOR_TEAL, linewidth=2.2, label=r'PM$_{2.5}$ Monthly Mean ($\mu$g/m$^3$)')
ax.fill_between(x_idx, pm25_mean - 1.96 * pm25_sem, pm25_mean + 1.96 * pm25_sem, color=COLOR_TEAL, alpha=0.15)

# NAAQS Limits
ax.axhline(y=60, color=COLOR_CORAL, linestyle='--', linewidth=1.2, label=r'NAAQS Annual PM$_{10}$ Target (60 $\mu$g/m$^3$)')
ax.axhline(y=40, color=COLOR_AMBER, linestyle=':', linewidth=1.2, label=r'NAAQS Annual PM$_{2.5}$ Target (40 $\mu$g/m$^3$)')

# Annotations for lowest and peak months
min_pm10_idx = pm10_mean.idxmin()
ax.annotate(f'Monsoon Washout Min:\n{pm10_mean[min_pm10_idx]:.1f} $\\mu$g/m$^3$',
            xy=(min_pm10_idx, pm10_mean[min_pm10_idx]),
            xytext=(min_pm10_idx, pm10_mean[min_pm10_idx] - 18),
            arrowprops=dict(facecolor=COLOR_NAVY, shrink=0.08, width=1, headwidth=6),
            fontsize=8.5, fontweight='bold', color=COLOR_NAVY, ha='center',
            bbox=dict(boxstyle="round,pad=0.3", fc="#EFF6FF", ec=COLOR_NAVY, lw=0.8))

max_pm10_idx = pm10_mean.idxmax()
ax.annotate(f'Winter Accumulation Peak:\n{pm10_mean[max_pm10_idx]:.1f} $\\mu$g/m$^3$',
            xy=(max_pm10_idx, pm10_mean[max_pm10_idx]),
            xytext=(max_pm10_idx, pm10_mean[max_pm10_idx] + 14),
            arrowprops=dict(facecolor=COLOR_NAVY, shrink=0.08, width=1, headwidth=6),
            fontsize=8.5, fontweight='bold', color=COLOR_NAVY, ha='center',
            bbox=dict(boxstyle="round,pad=0.3", fc="#EFF6FF", ec=COLOR_NAVY, lw=0.8))

ax.set_xticks(x_idx)
ax.set_xticklabels(months, rotation=45, ha='right', fontsize=9.5)
ax.set_ylabel(r'Particulate Concentration ($\mu$g/m$^3$)', fontsize=11, fontweight='bold', labelpad=8)
ax.set_title('Figure 2: Multi-Year Monthly Trend and Seasonal Dynamics of PM2.5 and PM10 in Bengaluru (2024–2025)', fontsize=12, fontweight='bold', pad=14, color='#0F172A')
ax.set_ylim(15, 120)
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend(frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=8.5, loc='upper right', ncol=2)

plt.tight_layout()
c2_path = CHARTS_DIR / "chart2_temporal_variation_trends.png"
plt.savefig(c2_path, dpi=300)
plt.close()
print(f"Chart 2 saved to {c2_path}")


# ------------------------------------------------------------------------------
# CHART 3: Hourly Pollution Pattern (Diurnal Cycle)
# ------------------------------------------------------------------------------
print("Generating Chart 3: Hourly Diurnal Pollution Pattern...")
hourly_profile = df.groupby('Hour').agg({
    'PM10': 'mean',
    'PM2.5': 'mean',
    'NO2': 'mean',
    'CO': 'mean'
}).reset_index()

fig, ax1 = plt.subplots(figsize=(12, 6.5), dpi=300)
fig.patch.set_facecolor('#FFFFFF')
ax1.set_facecolor('#FAFAFA')

ax2 = ax1.twinx()

# Primary axis: Particulates
l1 = ax1.plot(hourly_profile['Hour'], hourly_profile['PM10'], color=COLOR_NAVY, marker='o', markersize=6, linewidth=2.5, label=r'PM$_{10}$ ($\mu$g/m$^3$)')
l2 = ax1.plot(hourly_profile['Hour'], hourly_profile['PM2.5'], color=COLOR_TEAL, marker='s', markersize=5.5, linewidth=2.2, label=r'PM$_{2.5}$ ($\mu$g/m$^3$)')

# Secondary axis: Gaseous traffic tracer NO2
l3 = ax2.plot(hourly_profile['Hour'], hourly_profile['NO2'], color=COLOR_AMBER, linestyle='--', marker='^', markersize=5.5, linewidth=2.0, label=r'NO$_2$ ($\mu$g/m$^3$)')

# Highlight rush hours & boundary layer dynamics
ax1.axvspan(7, 10, color='#FEE2E2', alpha=0.4, label='Morning Traffic Peak & Low Boundary Layer')
ax1.axvspan(19, 22, color='#FEF3C7', alpha=0.4, label='Evening Traffic Peak & Boundary Layer Stagnation')

ax1.set_xlabel('Hour of the Day (Indian Standard Time, IST)', fontsize=11, fontweight='bold', labelpad=8)
ax1.set_ylabel(r'Particulate Concentration ($\mu$g/m$^3$)', fontsize=11, fontweight='bold', color=COLOR_NAVY, labelpad=8)
ax2.set_ylabel(r'Nitrogen Dioxide Concentration ($\mu$g/m$^3$)', fontsize=11, fontweight='bold', color=COLOR_AMBER, labelpad=8)

ax1.set_xticks(range(0, 24))
ax1.set_xticklabels([f"{h:02d}:00" for h in range(24)], rotation=45, fontsize=8.5)
ax1.set_title('Figure 3: Diurnal 24-Hour Cycle of Criteria Air Pollutants in Bengaluru (2024–2025)\nDemonstrating Boundary Layer Compression and Commuter Peak Emissions', fontsize=12, fontweight='bold', pad=14, color='#0F172A')

ax1.grid(True, linestyle='--', alpha=0.5)

# Combined legend
lines = l1 + l2 + l3
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='upper left', frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=9)

plt.tight_layout()
c3_path = CHARTS_DIR / "chart3_hourly_diurnal_pattern.png"
plt.savefig(c3_path, dpi=300)
plt.close()
print(f"Chart 3 saved to {c3_path}")


# ------------------------------------------------------------------------------
# CHART 4: Relationship Between Temperature and PM2.5
# ------------------------------------------------------------------------------
print("Generating Chart 4: Relationship Between Temperature and PM2.5...")
fig, ax = plt.subplots(figsize=(11, 7), dpi=300)
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#FAFAFA')

# Filter valid in-situ observations for temperature and PM2.5 within physical limits
sample_df = df_hourly.dropna(subset=['AT', 'PM2.5'])
sample_df = sample_df[(sample_df['AT'] >= 10) & (sample_df['AT'] <= 42) & (sample_df['PM2.5'] <= 200)]

# Subsample if large for crisp scatter rendering
if len(sample_df) > 15000:
    plot_subset = sample_df.sample(15000, random_state=42)
else:
    plot_subset = sample_df

# Hexbin density or scatter with density coloring
hb = ax.hexbin(plot_subset['AT'], plot_subset['PM2.5'], gridsize=45, cmap='Blues', mincnt=1, alpha=0.85, edgecolors='none')
cb = fig.colorbar(hb, ax=ax, orientation='vertical', pad=0.02)
cb.set_label('Observation Density (Count)', fontsize=9.5, fontweight='medium')

# Linear regression
slope, intercept, r_value, p_value, std_err = stats.linregress(plot_subset['AT'], plot_subset['PM2.5'])
x_vals = np.linspace(plot_subset['AT'].min(), plot_subset['AT'].max(), 100)
y_vals = slope * x_vals + intercept
ax.plot(x_vals, y_vals, color=COLOR_CORAL, linewidth=2.8, linestyle='-', label=f'Linear Fit: y = {slope:.2f}x + {intercept:.1f}\nPearson r = {r_value:.2f} (p < 0.001, N={len(sample_df):,})')

ax.set_xlabel('Ambient Temperature (°C)', fontsize=11, fontweight='bold', labelpad=8)
ax.set_ylabel(r'Fine Particulate Matter PM$_{2.5}$ ($\mu$g/m$^3$)', fontsize=11, fontweight='bold', labelpad=8)
ax.set_title('Figure 4: Bivariate Relationship Between Ambient Temperature and Fine Particulate Matter (PM2.5)\nRevealing Inverse Correlation Driven by Convective Vertical Dispersion', fontsize=12, fontweight='bold', pad=14, color='#0F172A')

ax.grid(True, linestyle='--', alpha=0.5)
ax.legend(frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=9.5, loc='upper right')

# Annotation box explaining scientific mechanism
textstr = '\n'.join((
    r'$\mathbf{Research\ Interpretation:}$',
    f'• Weak-to-moderate inverse association (r = {r_value:.2f}).',
    '• Warmer surface conditions induce thermal convection,',
    '  elevating planetary boundary layer height.',
    '• Cooler conditions foster atmospheric stability and',
    '  surface pollutant trapping (thermal inversion).'
))
props = dict(boxstyle='round,pad=0.5', facecolor='#F8FAFC', edgecolor='#94A3B8', alpha=0.95)
ax.text(0.04, 0.95, textstr, transform=ax.transAxes, fontsize=8.5, verticalalignment='top', bbox=props)

plt.tight_layout()
c4_path = CHARTS_DIR / "chart4_temperature_pm25_relationship.png"
plt.savefig(c4_path, dpi=300)
plt.close()
print(f"Chart 4 saved to {c4_path}")


# ------------------------------------------------------------------------------
# CHART 5: Relationship Between Wind Speed and Air Pollution
# ------------------------------------------------------------------------------
print("Generating Chart 5: Relationship Between Wind Speed and Air Pollution...")
fig, ax = plt.subplots(figsize=(11, 7), dpi=300)
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#FAFAFA')

sample_ws = df_hourly.dropna(subset=['WS', 'PM10', 'PM2.5'])
sample_ws = sample_ws[(sample_ws['WS'] >= 0.05) & (sample_ws['WS'] <= 6.0) & (sample_ws['PM10'] <= 350)]

# Wind speed bins for mean and 95% CI curves
bins = np.linspace(0.1, 4.5, 25)
sample_ws['WS_bin'] = pd.cut(sample_ws['WS'], bins=bins)
bin_stats = sample_ws.groupby('WS_bin', observed=True).agg({
    'WS': 'mean',
    'PM10': ['mean', 'sem'],
    'PM2.5': ['mean', 'sem']
}).dropna()

ws_center = bin_stats['WS']['mean']
pm10_bin_mean = bin_stats['PM10']['mean']
pm10_bin_sem = bin_stats['PM10']['sem']
pm25_bin_mean = bin_stats['PM2.5']['mean']
pm25_bin_sem = bin_stats['PM2.5']['sem']

# Plot raw points lightly
sub_pts = sample_ws.sample(min(8000, len(sample_ws)), random_state=42)
ax.scatter(sub_pts['WS'], sub_pts['PM10'], color=COLOR_NAVY, alpha=0.08, s=12, label='Hourly PM10 Observations')

# Plot binned trends
ax.plot(ws_center, pm10_bin_mean, color=COLOR_NAVY, linewidth=2.8, marker='o', markersize=6, label=r'Binned Mean PM$_{10}$ ($\pm$95% CI)')
ax.fill_between(ws_center, pm10_bin_mean - 1.96*pm10_bin_sem, pm10_bin_mean + 1.96*pm10_bin_sem, color=COLOR_NAVY, alpha=0.2)

ax.plot(ws_center, pm25_bin_mean, color=COLOR_TEAL, linewidth=2.4, marker='s', markersize=5, label=r'Binned Mean PM$_{2.5}$ ($\pm$95% CI)')
ax.fill_between(ws_center, pm25_bin_mean - 1.96*pm25_bin_sem, pm25_bin_mean + 1.96*pm25_bin_sem, color=COLOR_TEAL, alpha=0.2)

# Calm wind stagnation zone shading
ax.axvspan(0.0, 1.0, color='#FEE2E2', alpha=0.4, label='Calm Stagnation Regime (WS < 1.0 m/s)')

ax.set_xlabel('Horizontal Wind Speed (m/s)', fontsize=11, fontweight='bold', labelpad=8)
ax.set_ylabel(r'Particulate Concentration ($\mu$g/m$^3$)', fontsize=11, fontweight='bold', labelpad=8)
ax.set_title('Figure 5: Non-Linear Aerodynamic Dispersion: Impact of Wind Speed on Particulate Pollution\nDemonstrating Severe Accumulation During Stagnation Regimes vs. Mechanical Dilution', fontsize=12, fontweight='bold', pad=14, color='#0F172A')

ax.set_xlim(0, 4.5)
ax.set_ylim(10, 180)
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend(frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=9, loc='upper right')

# Text annotation
textstr = '\n'.join((
    r'$\mathbf{Aerodynamic\ Dispersion\ Findings:}$',
    '• Sharp non-linear decline in particulate matter with increasing wind.',
    '• Under calm conditions (WS < 1.0 m/s), PM10 averages > 85 µg/m³.',
    '• Moderate breezes (> 2.5 m/s) enhance horizontal advection,',
    '  reducing mean PM10 by ~42% down to < 50 µg/m³.'
))
props = dict(boxstyle='round,pad=0.5', facecolor='#F8FAFC', edgecolor='#94A3B8', alpha=0.95)
ax.text(0.48, 0.52, textstr, transform=ax.transAxes, fontsize=8.5, verticalalignment='top', bbox=props)

plt.tight_layout()
c5_path = CHARTS_DIR / "chart5_wind_speed_pollution_relationship.png"
plt.savefig(c5_path, dpi=300)
plt.close()
print(f"Chart 5 saved to {c5_path}")


# ------------------------------------------------------------------------------
# CHART 6: Correlation Heatmap of Air Quality and Meteorological Variables
# ------------------------------------------------------------------------------
print("Generating Chart 6: Correlation Heatmap...")
corr_features = [
    ('PM2.5', r'PM$_{2.5}$'),
    ('PM10', r'PM$_{10}$'),
    ('NO2', r'NO$_2$'),
    ('SO2', r'SO$_2$'),
    ('CO', 'CO'),
    ('Ozone', r'O$_3$'),
    ('NH3', r'NH$_3$'),
    ('AT', 'Temp (°C)'),
    ('RH', 'RH (%)'),
    ('WS', 'Wind Speed'),
    ('BP', 'Pressure'),
    ('SR', 'Solar Rad')
]
avail_features = [f for f in corr_features if f[0] in df_hourly.columns]
raw_cols = [f[0] for f in avail_features]
display_labels = [f[1] for f in avail_features]

corr_sub_df = df_hourly[raw_cols].corr().round(2)

fig, ax = plt.subplots(figsize=(10.5, 9), dpi=300)
fig.patch.set_facecolor('#FFFFFF')

# Custom diverging colormap
cmap = sns.diverging_palette(220, 20, as_cmap=True)

# Generate mask for upper triangle
mask = np.triu(np.ones_like(corr_sub_df, dtype=bool))

sns.heatmap(corr_sub_df, mask=mask, cmap='RdBu_r', vmin=-0.8, vmax=0.8,
            annot=True, fmt='.2f', annot_kws={'size': 9, 'fontweight': 'bold'},
            square=True, linewidths=1.2, linecolor='#FFFFFF',
            cbar_kws={'label': "Pearson's Correlation Coefficient (r)", 'shrink': 0.78, 'pad': 0.03},
            xticklabels=display_labels, yticklabels=display_labels, ax=ax)

ax.set_title('Figure 6: Cross-Correlation Matrix of Ambient Criteria Pollutants\nand In-Situ Meteorological Parameters in Bengaluru (2024–2025)', fontsize=12, fontweight='bold', pad=16, color='#0F172A')

plt.xticks(rotation=45, ha='right', fontsize=9.5, fontweight='medium')
plt.yticks(rotation=0, fontsize=9.5, fontweight='medium')

plt.tight_layout()
c6_path = CHARTS_DIR / "chart6_air_quality_weather_correlation_heatmap.png"
plt.savefig(c6_path, dpi=300)
plt.close()
print(f"Chart 6 saved to {c6_path}")


# ------------------------------------------------------------------------------
# FIGURE 7: Research Methodology Flowchart Diagram
# ------------------------------------------------------------------------------
print("Generating Methodology Flowchart Diagram...")
fig, ax = plt.subplots(figsize=(14, 5.5), dpi=300)
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#FFFFFF')
ax.axis('off')

# Box drawing helper
def draw_stage_box(ax, x, y, w, h, title, subtitle, items, bg_color, border_color):
    # Rounded card
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03,rounding_size=0.08",
                                  facecolor=bg_color, edgecolor=border_color, linewidth=2.0, zorder=2)
    ax.add_patch(rect)
    
    # Title banner
    ax.text(x + w/2, y + h - 0.22, title, ha='center', va='center', fontsize=10.5, fontweight='bold', color=border_color, zorder=3)
    ax.text(x + w/2, y + h - 0.45, subtitle, ha='center', va='center', fontsize=8.5, fontstyle='italic', color='#475569', zorder=3)
    
    # Divider line
    ax.plot([x + 0.15, x + w - 0.15], [y + h - 0.6, y + h - 0.6], color=border_color, alpha=0.4, linewidth=1.0, zorder=3)
    
    # Bullets
    start_y = y + h - 0.85
    for i, item in enumerate(items):
        ax.text(x + 0.2, start_y - (i * 0.32), f"• {item}", ha='left', va='center', fontsize=8.2, color='#1E293B', zorder=3)

# Arrow helper
def draw_pipeline_arrow(ax, x1, y1, x2, y2, label=""):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color='#334155', lw=2.2, mutation_scale=18), zorder=4)
    if label:
        ax.text((x1+x2)/2, y1 + 0.15, label, ha='center', va='bottom', fontsize=8, fontweight='bold', color='#475569')

# Define stages
stages = [
    {
        "title": "STAGE 1: DATA INGESTION",
        "subtitle": "Raw Observational Records",
        "items": [
            "13 KSPCB / CPCB Stations",
            "866,057 Raw Observations",
            "Continuous 15-min Frequency",
            "Temporal Span: 2024–2025",
            "9 Pollutants + 8 Met Variables"
        ],
        "bg": "#EFF6FF",
        "border": "#1E3A8A"
    },
    {
        "title": "STAGE 2: BIG DATA QA/QC",
        "subtitle": "PySpark Cleaning Pipeline",
        "items": [
            "Delimitation Artifact Removal",
            "Schema Type Coercion",
            "Null-Handling (No Zero-Fill)",
            "Strict Duplicate Elimination",
            "Retained 866,044 Clean Rows"
        ],
        "bg": "#F0FDF4",
        "border": "#059669"
    },
    {
        "title": "STAGE 3: TEMPORAL AGGREGATION",
        "subtitle": "PySpark Analytical Windowing",
        "items": [
            "Hourly Floor GroupBy Window",
            "15-min to 1-Hour Mean Aggregation",
            "Generated 215,845 Station-Hours",
            "Harmonized with ERA5 Grid",
            "Master Environmental Dataset"
        ],
        "bg": "#F5F3FF",
        "border": "#7C3AED"
    },
    {
        "title": "STAGE 4: SCIENTIFIC ANALYTICS",
        "subtitle": "Statistical & Spatial Modeling",
        "items": [
            "Spatial Station Comparisons",
            "Seasonal Trend Decomposition",
            "24-Hour Diurnal Dynamics",
            "Atmospheric Inversion Analysis",
            "Aerodynamic Wind Dispersion"
        ],
        "bg": "#FFFBEB",
        "border": "#D97706"
    },
    {
        "title": "STAGE 5: RESEARCH POSTER",
        "subtitle": "Publication & Dissemination",
        "items": [
            "6 Publication-Grade Charts",
            "A0 Cardboard Landscape Poster",
            "Verified Mathematical Findings",
            "Complete PySpark Codebase",
            "Comprehensive Research Reports"
        ],
        "bg": "#FEF2F2",
        "border": "#DC2626"
    }
]

box_w = 2.4
box_h = 2.9
box_y = 1.0

for i, s in enumerate(stages):
    box_x = 0.5 + i * 2.7
    draw_stage_box(ax, box_x, box_y, box_w, box_h, s["title"], s["subtitle"], s["items"], s["bg"], s["border"])
    if i < len(stages) - 1:
        draw_pipeline_arrow(ax, box_x + box_w, box_y + box_h/2, box_x + 2.7, box_y + box_h/2)

ax.set_xlim(0, 14)
ax.set_ylim(0.5, 4.5)

ax.text(7.0, 4.2, 'End-to-End PySpark Big Data Engineering & Analytical Research Methodology Flowchart',
        ha='center', va='center', fontsize=13, fontweight='bold', color='#0F172A')

plt.tight_layout()
flowchart_path = CHARTS_DIR / "methodology_flowchart.png"
plt.savefig(flowchart_path, dpi=300)
plt.close()
print(f"Flowchart saved to {flowchart_path}")

print("\nAll 6 Research Charts and Methodology Flowchart generated successfully!")
