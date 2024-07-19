import geopandas as gpd
import pandas as pd
import json
from datetime import datetime

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, pd.Timestamp)):
            return obj.isoformat()
        elif isinstance(obj, gpd.GeoSeries):
            return obj.to_wkt().tolist()
        return super().default(obj)

def write_dataframe_info(file, df, name):
    file.write(f"\n{name} Information:\n")
    file.write(f"Shape: {df.shape}\n")
    file.write("\nColumns:\n")
    file.write(str(df.columns.tolist()) + "\n")
    file.write("\nData Types:\n")
    file.write(str(df.dtypes) + "\n")
    file.write("\nFirst 5 rows:\n")
    file.write(df.head().to_string() + "\n")

def write_geojson_sample(file, gdf):
    file.write("\nGeoJSON Sample (first 2 features):\n")
    geojson_sample = json.loads(gdf.head(2).to_json(cls=CustomJSONEncoder))
    file.write(json.dumps(geojson_sample, indent=2) + "\n")

# Open a file to write the output
with open("data_extraction_results.txt", "w", encoding="utf-8") as f:
    # Load GeoJSON file
    f.write("Loading GeoJSON file...\n")
    gdf = gpd.read_file("src/geneva_communes.geojson")
    write_dataframe_info(f, gdf, "GeoJSON")
    write_geojson_sample(f, gdf)

    # Load CSV file
    f.write("\nLoading CSV file...\n")
    df = pd.read_csv("src/density.csv")
    write_dataframe_info(f, df, "CSV")

    # Check for any Timestamp columns in GeoJSON
    timestamp_columns = gdf.select_dtypes(include=['datetime64']).columns
    if len(timestamp_columns) > 0:
        f.write("\nTimestamp columns found in GeoJSON:\n")
        f.write(str(timestamp_columns.tolist()) + "\n")
        f.write("\nSample values:\n")
        f.write(gdf[timestamp_columns].head().to_string() + "\n")
    else:
        f.write("\nNo Timestamp columns found in GeoJSON.\n")

    # Check for any potential issues in name matching
    f.write("\nChecking for name matching issues...\n")
    geojson_names = set(gdf['name'])
    csv_names = set(df['Nom'])
    f.write(f"Names only in GeoJSON: {geojson_names - csv_names}\n")
    f.write(f"Names only in CSV: {csv_names - geojson_names}\n")

print("Data extraction complete. Results written to 'data_extraction_results.txt'")