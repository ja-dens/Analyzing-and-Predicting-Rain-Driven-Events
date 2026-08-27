import pandas as pd
from pathlib import Path

# === CONFIGURATION ===
project_root = Path(__file__).resolve().parents[2]
input_folder = project_root / 'data' / 'raw' / 'noaa_lcd'
output_file = project_root / 'data' / 'processed' / 'rain_data.csv'
selected_columns = ['DATE', 'HourlyAltimeterSetting', 'HourlyDewPointTemperature',
                    'HourlyDryBulbTemperature', 'HourlyPrecipitation',
                    'HourlyPressureChange', 'HourlyRelativeHumidity',
                    'HourlyStationPressure', 'HourlyVisibility',
                    'HourlyWetBulbTemperature', 'HourlyWindSpeed']
na_strategy = 'fill'  # options: 'drop', 'fill'

if not input_folder.exists():
    raise FileNotFoundError(
        f"NOAA input folder not found: {input_folder}. "
        "See data/README.md for setup instructions."
    )

# === PROCESSING ===
all_dfs = []
csv_files = sorted(input_folder.glob('*.csv'))

for file_path in csv_files:
    filename = file_path.name
    location_name = file_path.stem

    try:
        df = pd.read_csv(file_path)

        if 'REPORT_TYPE' in df.columns:
            df = df[df['REPORT_TYPE'] != 'SOD']

        # Clean and standardize known messy columns
        if 'HourlyPrecipitation' in df.columns:
            df['HourlyPrecipitation'] = df['HourlyPrecipitation'].replace('T', 0)
            df = df[~df['HourlyPrecipitation'].astype(str).str.contains('s', na=False)]

        if 'HourlyVisibility' in df.columns:
            df['HourlyVisibility'] = df['HourlyVisibility'].astype(str).str.replace('V', '', regex=False)

        if 'HourlyDryBulbTemperature' in df.columns:
            df['HourlyDryBulbTemperature'] = df['HourlyDryBulbTemperature'].astype(str).str.replace('s', '', regex=False)

        # Clean all selected numeric columns
        for col in selected_columns:
            if col in df.columns and col != 'DATE':
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Keep only selected columns
        columns_to_keep = [col for col in selected_columns if col in df.columns]
        df = df[columns_to_keep]

        # Add location
        df['Location'] = location_name

        # Report missingness

        # Handle NA
        if na_strategy == 'drop':
            df = df.dropna()
        elif na_strategy == 'fill':
            fill_strategies = {
                'HourlyAltimeterSetting': 'bothfill',
                'HourlyDewPointTemperature': 'bothfill',
                'HourlyDryBulbTemperature': 'bothfill',
                'HourlyPrecipitation': 0,
                'HourlyPressureChange': 0,
                'HourlyRelativeHumidity': 'bothfill',
                'HourlyStationPressure': 'bothfill',
                'HourlyVisibility': 'bothfill',
                'HourlyWetBulbTemperature': 'bothfill',
                'HourlyWindSpeed': 'bothfill'
            }

            for col, strategy in fill_strategies.items():
                if col not in df.columns:
                    continue
                if strategy == 'bothfill':
                    df[col] = df[col].ffill().bfill()
                else:
                    df[col] = df[col].fillna(strategy)

        all_dfs.append(df)
        print(f"✅ Processed: {filename} — Rows: {len(df)}")

    except Exception as e:
        print(f"⚠️ Error reading {file_path}: {e}")

# === MERGE ===
if all_dfs:
    merged_df = pd.concat(all_dfs, ignore_index=True)

    merged_df['DATE'] = pd.to_datetime(merged_df['DATE'], errors='coerce')
    merged_df['Year'] = merged_df['DATE'].dt.year
    merged_df['Month'] = merged_df['DATE'].dt.month
    merged_df['Day'] = merged_df['DATE'].dt.day
    merged_df['Hour'] = merged_df['DATE'].dt.hour

    aggregation_methods = {
        'HourlyAltimeterSetting': 'mean',
        'HourlyDewPointTemperature': 'mean',
        'HourlyDryBulbTemperature': 'mean',
        'HourlyPrecipitation': 'mean',
        'HourlyPressureChange': 'mean',
        'HourlyRelativeHumidity': 'mean',
        'HourlyStationPressure': 'mean',
        'HourlyVisibility': 'mean',
        'HourlyWetBulbTemperature': 'mean',
        'HourlyWindSpeed': 'mean'
    }

    for col in aggregation_methods:
        if col in merged_df.columns:
            merged_df[col] = pd.to_numeric(merged_df[col], errors='coerce')

    merged_df = merged_df.groupby(['Location', 'Year', 'Month', 'Day', 'Hour']).agg(aggregation_methods).reset_index()

    # Optional grouped fill again after merge
    merged_df = merged_df.sort_values(by=['Location', 'Year', 'Month', 'Day', 'Hour'])
    merged_df = merged_df.groupby('Location').apply(lambda group: group.ffill().bfill()).reset_index(drop=True)

    merged_df['DATE'] = pd.to_datetime(merged_df[['Year', 'Month', 'Day', 'Hour']])
    date_cols = ['DATE', 'Year', 'Month', 'Day', 'Hour']
    metric_cols = [col for col in merged_df.columns if col not in date_cols + ['Location']]
    merged_df = merged_df[['Location'] + date_cols + metric_cols]
    merged_df = merged_df.drop('DATE', axis=1)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    merged_df.to_csv(output_file, index=False)
    print(f"✅ Merged data saved to: {output_file}")
else:
    print("❌ No valid CSV files were processed.")
