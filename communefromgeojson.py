import json

def extract_commune_names(geojson_file):
    with open(geojson_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    commune_names = []
    for feature in data['features']:
        name = feature['properties'].get('name')
        if name:
            commune_names.append(name)
    
    return commune_names

# Use the function
geojson_file = 'src/geneva_communes.geojson'
names = extract_commune_names(geojson_file)

print("Commune names in GeoJSON file:")
for name in sorted(names):
    print(name)

print(f"\nTotal number of communes: {len(names)}")