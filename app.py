import streamlit as st
import folium
from streamlit_folium import folium_static
import geopandas as gpd

# Set page title
st.set_page_config(page_title="Geneva Ambulance Locations")

# Title
st.title("Geneva Ambulance Locations")

# Create a map centered on Geneva
m = folium.Map(location=[46.2044, 6.1432], zoom_start=12)

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
        icon=folium.Icon(color="red", icon="ambulance", prefix='fa')
    ).add_to(m)

# Load GeoJSON data for Geneva (you'll need to provide the correct file path)
# gdf = gpd.read_file("path_to_your_geojson_file.geojson")

# For now, we'll use a placeholder for the density overlay
# In the future, replace this with actual data visualization
folium.Circle(
    radius=3000,
    location=[46.2044, 6.1432],
    popup="Population Density",
    color="crimson",
    fill=True,
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