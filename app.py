import streamlit as st
import folium
from streamlit_folium import folium_static
import geopandas as gpd
import pandas as pd
import json
from datetime import datetime
import random

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, pd.Timestamp)):
        return obj.isoformat()
    if isinstance(obj, gpd.GeoSeries):
        return obj.to_json()
    raise TypeError(f"Type {type(obj)} not serializable")

st.set_page_config(page_title="TCS Swiss Ambulance Rescue Geneva Simulation", layout="wide")
st.title("TCS Swiss Ambulance Rescue Geneva Simulation")

# Load and process data
@st.cache_data
def load_data():
    gdf = gpd.read_file("src/geneva_communes.geojson").to_crs("EPSG:4326")
    density_df = pd.read_csv("src/density.csv")
    
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
    
    gdf['name'] = gdf['name'].map(lambda x: name_mapping.get(x, x))
    gdf = gdf.merge(density_df, left_on="name", right_on="Nom", how="left")
    
    return gdf

gdf = load_data()

# TCS Swiss Ambulance Rescue Geneva Information
tcs_info = {
    "total_employees": 70,
    "total_vehicles": 15,
    "bases": [
        {"name": "Base d'Alcide-Jentzer", "coords": [46.1922208, 6.1458217], "ambulances": 7, "teams": 3},
        {"name": "Base des Eaux-Vives", "coords": [46.2014450, 6.1665700], "ambulances": 4, "teams": 2},
        {"name": "Base de Ferrier", "coords": [46.2135260, 6.1489360], "ambulances": 1, "teams": 1}
    ],
    "annual_interventions": 30000,
    "emergency_interventions": 9000,
    "secondary_interventions": 5500
}

# Create map
m = folium.Map(location=[46.2044, 6.1432], zoom_start=11)

# Add choropleth layer
folium.Choropleth(
    geo_data=json.loads(gdf.to_json(default=json_serial)),
    name="Population Density",
    data=gdf,
    columns=["name", "Densité (hab./km2)"],
    key_on="feature.properties.name",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Population Density (hab./km2)",
).add_to(m)

# Add base markers
for base in tcs_info["bases"]:
    folium.Marker(
        base["coords"],
        popup=f"{base['name']}<br>Ambulances: {base['ambulances']}<br>Teams: {base['teams']}",
        icon=folium.Icon(color="blue", icon="ambulance", prefix='fa')
    ).add_to(m)

# Simulate emergency calls
def simulate_emergency_calls(num_calls):
    calls = []
    for _ in range(num_calls):
        commune = random.choice(gdf['name'].tolist())
        coords = gdf[gdf['name'] == commune].geometry.centroid.iloc[0]
        calls.append({
            "commune": commune,
            "coords": [coords.y, coords.x]
        })
    return calls

# Add emergency call markers
emergency_calls = simulate_emergency_calls(10)
for call in emergency_calls:
    folium.Marker(
        call["coords"],
        popup=f"Emergency in {call['commune']}",
        icon=folium.Icon(color="red", icon="exclamation", prefix='fa')
    ).add_to(m)

# Display map and information
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Geneva Map with Ambulance Bases and Simulated Emergency Calls")
    folium_static(m)

with col2:
    st.subheader("TCS Swiss Ambulance Rescue Geneva Info")
    st.write(f"Total Employees: {tcs_info['total_employees']}")
    st.write(f"Total Vehicles: {tcs_info['total_vehicles']}")
    st.write(f"Annual Interventions: {tcs_info['annual_interventions']}")
    st.write(f"Emergency Interventions: {tcs_info['emergency_interventions']}")
    st.write(f"Secondary Interventions: {tcs_info['secondary_interventions']}")
    
    st.subheader("Ambulance Bases")
    for base in tcs_info["bases"]:
        st.write(f"{base['name']}:")
        st.write(f"  Ambulances: {base['ambulances']}")
        st.write(f"  Teams: {base['teams']}")

# Simulation parameters
st.sidebar.title("Simulation Parameters")
num_ambulances = st.sidebar.slider("Number of Ambulances", 1, tcs_info['total_vehicles'], tcs_info['total_vehicles'])
population_size = st.sidebar.number_input("Population Size", 100, 1000, 500)
num_generations = st.sidebar.number_input("Number of Generations", 10, 1000, 100)
mutation_rate = st.sidebar.slider("Mutation Rate", 0.0, 1.0, 0.01)
crossover_rate = st.sidebar.slider("Crossover Rate", 0.0, 1.0, 0.8)

# Placeholder for genetic algorithm optimization
st.subheader("Genetic Algorithm Optimization")
st.write("This section would implement the genetic algorithm to optimize ambulance locations based on population density and emergency call distribution.")

# Additional analysis and visualizations
st.subheader("Additional Analysis")
st.write("Here you could add more visualizations, such as:")
st.write("- Heatmap of emergency calls")
st.write("- Response time analysis")
st.write("- Ambulance utilization statistics")

# Data source information
st.markdown("""
## Data Sources
- Commune boundaries: GeoJSON file in src/geneva_communes.geojson
- Population density: CSV file in src/density.csv
- TCS Swiss Ambulance Rescue Geneva information: Based on provided details
- Emergency calls: Simulated based on population density
""")