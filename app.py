import streamlit as st
import folium
from streamlit_folium import folium_static
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon

# Load communes data
communes_df = pd.read_csv("src/geneve_communes.csv", sep=";")

# Load density data
density_df = pd.read_csv("src/density.csv")

# Create geometry from SHAPE.AREA and SHAPE.LEN (this is an approximation)
communes_df['geometry'] = communes_df.apply(lambda row: Polygon([(0, 0), (row['SHAPE.LEN'], 0), 
                                                                 (row['SHAPE.LEN'], row['SHAPE.AREA']/row['SHAPE.LEN']), 
                                                                 (0, row['SHAPE.AREA']/row['SHAPE.LEN'])]), axis=1)

# Create GeoDataFrame
gdf = gpd.GeoDataFrame(communes_df, geometry='geometry')

# Merge with density data
gdf = gdf.merge(density_df, left_on="NO_COM_FEDERAL", right_on="N° OFS1", how="left")

# Set page title
st.set_page_config(page_title="Geneva Ambulance Locations and Population Density")

# Title
st.title("Geneva Ambulance Locations and Population Density")

# Create a map centered on Geneva
m = folium.Map(location=[46.2044, 6.1432], zoom_start=11)

# Add choropleth layer
folium.Choropleth(
    geo_data=gdf,
    name="Population Density",
    data=gdf,
    columns=["COMMUNE", "Densité (hab./km2)"],
    key_on="feature.properties.COMMUNE",
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
        icon=folium.Icon(color="red", icon="ambulance", prefix='fa')
    ).add_to(m)

# Add layer control
folium.LayerControl().add_to(m)

# Display the map
folium_static(m)

# Sidebar for future parameter controls
st.sidebar.title("Parameters")
st.sidebar.slider("Number of Ambulances", 1, 10, 3)
st.sidebar.number_input("Population Size", 100, 1000, 500)
st.sidebar.number_input("Number of Generations", 10, 1000, 100)
st.sidebar.slider("Mutation Rate", 0.0, 1.0, 0.01)
st.sidebar.slider("Crossover Rate", 0.0, 1.0, 0.8)

# Explanation of the data
st.markdown("""
## Population Density Map

This map shows the population density of Geneva's communes, with darker colors indicating higher density areas. 
The red ambulance icons show the current locations of ambulance bases.

Data sources:
- Commune boundaries: CSV file in src/geneve_communes.csv
- Population density: CSV file in src/density.csv
- Ambulance locations: Provided coordinates

Note: The commune boundaries are approximated based on area and length data. For more accurate representations, a proper GeoJSON file would be needed.

Next steps could include:
1. Implementing the genetic algorithm to optimize ambulance locations based on population density.
2. Adding more interactive elements to allow users to see the impact of different ambulance placements.
3. Incorporating additional factors such as road networks and historical emergency call data.
""")