import streamlit as st
import folium
from streamlit_folium import folium_static
import geopandas as gpd
import pandas as pd
import json

st.set_page_config(page_title="Geneva Ambulance Locations and Population Density")
st.title("Geneva Ambulance Locations and Population Density")

try:
    # Load GeoJSON data
    gdf = gpd.read_file("src/geneva_communes.geojson")
    
    # Check if CRS is set, if not, set it to EPSG:4326 (WGS84)
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    
    # Ensure the GeoDataFrame is in EPSG:4326
    gdf = gdf.to_crs("EPSG:4326")

    # Load density data
    density_df = pd.read_csv("src/density.csv")

    # Merge with density data
    gdf = gdf.merge(density_df, left_on="name", right_on="Nom", how="left")

    # Create a map centered on Geneva
    m = folium.Map(location=[46.2044, 6.1432], zoom_start=11)

    # Add choropleth layer
    folium.Choropleth(
        geo_data=gdf.__geo_interface__,
        name="Population Density",
        data=gdf,
        columns=["name", "Densité (hab./km2)"],
        key_on="feature.properties.name",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Population Density (hab./km2)",
    ).add_to(m)

    # Ambulance base locations
    bases = [
        {"name": "Base d'Alcide-Jentzer", "coords": [46.1922208, 6.1458217]},
        {"name": "Base des Eaux-Vives", "coords": [46.2014450, 6.1665700]},
        {"name": "Base de Ferrier", "coords": [46.2135260, 6.1489360]}
    ]

    # Add markers for each ambulance base
    for base in bases:
        folium.Marker(
            base["coords"],
            popup=base["name"],
            icon=folium.Icon(color="blue", icon="ambulance", prefix='fa')
        ).add_to(m)

    # Display the map
    folium_static(m)

    # Sidebar for future parameter controls
    st.sidebar.title("Parameters")
    st.sidebar.slider("Number of Ambulances", 1, 10, 3)
    st.sidebar.number_input("Population Size", 100, 1000, 500)
    st.sidebar.number_input("Number of Generations", 10, 1000, 100)
    st.sidebar.slider("Mutation Rate", 0.0, 1.0, 0.01)
    st.sidebar.slider("Crossover Rate", 0.0, 1.0, 0.8)

except FileNotFoundError as e:
    st.error(f"Error: Could not find the file. Please check if the file paths are correct. Details: {e}")
except pd.errors.EmptyDataError:
    st.error("Error: The CSV file is empty. Please check the content of your density.csv file.")
except json.JSONDecodeError:
    st.error("Error: Invalid JSON in the GeoJSON file. Please check the content of your geneva_communes.geojson file.")
except ValueError as e:
    st.error(f"Error: There was a problem with the data. Details: {e}")
except Exception as e:
    st.error(f"An unexpected error occurred: {e}")

# Explanation of the data
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