# Data setup

The source and generated datasets are intentionally excluded from this public archive because they are large and, in the case of EM-DAT, subject to redistribution restrictions.

Create the following local directories after cloning the repository:

```text
data/
  raw/
    noaa_lcd/
      AK.csv
      AL.csv
      ...
    emdat_data.csv
  processed/
```

## NOAA weather files

Download the appropriate Local Climatological Data subset from the [NOAA National Centers for Environmental Information](https://www.ncei.noaa.gov/products/land-based-station/local-climatological-data). Place the state-level CSV files in `data/raw/noaa_lcd/`.

The cleaning script uses each filename, without `.csv`, as its `Location` value. Preserve the two-letter state filenames used by the original project if you want the later joins to match.

Running `Code/Data Cleaning-Processing/handle.data.py` creates:

```text
data/processed/rain_data.csv
```

Record the exact NOAA dataset version, subset, and access date in any publication or reproduction.

## EM-DAT file

Obtain authorized access through the [EM-DAT public data portal](https://public.emdat.be/) and review its [terms of use](https://doc.emdat.be/docs/legal/terms-of-use/) before downloading or using the data. Place the authorized export at:

```text
data/raw/emdat_data.csv
```

The public repository must not include the downloaded EM-DAT export or derived event-level tables. Running the processing notebooks locally produces files such as:

```text
data/processed/states_extracted.csv
data/processed/disaster_events.csv
data/processed/weather_wide_pivot.csv
```

These paths are ignored by Git. Follow the current [EM-DAT citation policy](https://doc.emdat.be/docs/legal/citation-policy/) in any public use of the results.
