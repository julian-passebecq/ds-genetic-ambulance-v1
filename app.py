import streamlit as st
import folium
from streamlit_folium import folium_static
import geopandas as gpd
import pandas as pd
import json
from datetime import datetime

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, pd.Timestamp)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

st.set_page_config(page_title="Geneva Ambulance Locations and Population Density")
st.title("Geneva Ambulance Locations and Population Density")

try:
    st.write("Loading GeoJSON data...")
    gdf = gpd.read_file("src/geneva_communes.geojson")
    st.write(f"GeoJSON data loaded. Shape: {gdf.shape}")
    
    st.write("Ensuring GeoDataFrame is in EPSG:4326...")
    gdf = gdf.to_crs("EPSG:4326")
    
    st.write("Loading density data...")
    density_df = pd.read_csv("src/density.csv")
    st.write(f"Density data loaded. Shape: {density_df.shape}")

    name_mapping = {
        'Anières': 'Anières',
        'Carouge (GE)': 'Carouge',
        'Chène-Bourg': 'Chêne-Bourg',
        'Corsier (GE)': 'Corsier',
        'Céligny': 'Céligny',
        'Genève': 'Genève',
        'Le Grand-Saconnex': 'Le Grand-Saconnex',
        'Pregny-Chambésy': 'Pregny-Chambésy',
        'Vandoeuvres': 'Vandœuvres'
    }

    st.write("Applying name mapping...")
    gdf['name'] = gdf['name'].map(lambda x: name_mapping.get(x, x))

    st.write("Merging GeoDataFrame with density data...")
    gdf = gdf.merge(density_df, left_on="name", right_on="Nom", how="left")
    st.write(f"Merged data shape: {gdf.shape}")

    st.write("Creating map...")
    m = folium.Map(location=[46.2044, 6.1432], zoom_start=11)

    st.write("Converting GeoDataFrame to JSON...")
    geo_json = json.loads(gdf.to_json(), parse_constant=json_serial)
    
    st.write("Adding choropleth layer...")
    folium.Choropleth(
        geo_data=geo_json,
        name="Population Density",
        data=gdf,
        columns=["name", "Densité (hab./km2)"],
        key_on="feature.properties.name",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Population Density (hab./km2)",
    ).add_to(m)

    bases = [
        {"name": "Base d'Alcide-Jentzer", "coords": [46.1922208, 6.1458217]},
        {"name": "Base des Eaux-Vives", "coords": [46.2014450, 6.1665700]},
        {"name": "Base de Ferrier", "coords": [46.2135260, 6.1489360]}
    ]

    st.write("Adding ambulance base markers...")
    for base in bases:
        folium.Marker(
            base["coords"],
            popup=base["name"],
            icon=folium.Icon(color="blue", icon="ambulance", prefix='fa')
        ).add_to(m)

    st.write("Displaying map...")
    folium_static(m)

    st.sidebar.title("Parameters")
    st.sidebar.slider("Number of Ambulances", 1, 10, 3)
    st.sidebar.number_input("Population Size", 100, 1000, 500)
    st.sidebar.number_input("Number of Generations", 10, 1000, 100)
    st.sidebar.slider("Mutation Rate", 0.0, 1.0, 0.01)
    st.sidebar.slider("Crossover Rate", 0.0, 1.0, 0.8)

    unmatched = gdf[gdf['Densité (hab./km2)'].isna()]['name'].tolist()
    if unmatched:
        st.warning(f"The following communes were not matched: {', '.join(unmatched)}")

except FileNotFoundError as e:
    st.error(f"Error: Could not find the file. Please check if the file paths are correct. Details: {e}")
except pd.errors.EmptyDataError:
    st.error("Error: The CSV file is empty. Please check the content of your density.csv file.")
except json.JSONDecodeError as e:
    st.error(f"Error: Invalid JSON in the GeoJSON file. Please check the content of your geneva_communes.geojson file. Details: {e}")
except ValueError as e:
    st.error(f"Error: There was a problem with the data. Details: {e}")
except Exception as e:
    st.error(f"An unexpected error occurred: {e}")
    st.error("Full error details:")
    st.exception(e)

st.markdown("""
## Population Density Map

This map shows the geographical boundaries of Geneva's communes:
- Each commune is colored based on its population density (darker = higher density).
- The blue ambulance icons show the current locations of ambulance bases.

Data sources:
- Commune boundaries: GeoJSON file in src/geneva_communes.geojson
- Population density: CSV file in src/density.csv
- Ambulance locations: Provided coordinates

Next steps could include:
1. Implementing the genetic algorithm to optimize ambulance locations based on population density and geographic distribution.
2. Adding interactive elements to allow users to see the impact of different ambulance placements.
3. Incorporating additional factors such as road networks and historical emergency call data.
""")