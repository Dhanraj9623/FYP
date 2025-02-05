from flask import Flask, request, jsonify
from flask_cors import CORS
import ee
import requests

# Initialize Earth Engine
ee.Initialize(project='amazing-gearing-429214-q6')

app = Flask(__name__)
CORS(app) 

# NASA API endpoint
nasa_url = "https://power.larc.nasa.gov/api/temporal/climatology/point"

@app.route('/get_solar_data', methods=['POST'])
def get_solar_data():
    data = request.json
    polygon_coords = data.get('polygon')
    print(polygon_coords)
    
    region = ee.Geometry.Polygon([polygon_coords])

    buildings = ee.FeatureCollection("GOOGLE/Research/open-buildings/v3/polygons")
    
    # Filter buildings in selected region
    filtered_buildings = buildings.filterBounds(region)
    # Calculate total building area
    total_area = filtered_buildings.aggregate_sum("area_in_meters").getInfo()
    filtered_buildings2 = buildings.filterBounds(region).filter(ee.Filter.gte("confidence", 0.75))
    total_buildings = filtered_buildings2.size().getInfo()
    print(total_buildings)
    buildings_geo = filtered_buildings.aggregate_array("geometry").getInfo()
    
    centroid = region.centroid().getInfo()
    latitude = centroid['coordinates'][1]
    longitude = centroid['coordinates'][0]
    
    print(centroid)

    # Fetch solar data from NASA Power API
    params = {
        "parameters": "ALLSKY_SFC_SW_DWN",  # Solar radiation data
        "community": "SB",  # Science & Business
        "longitude": longitude,
        "latitude": latitude,
        "format": "JSON"
    }
    response = requests.get(nasa_url, params=params)
    solar_data = response.json()
    ann_solar_radiation = solar_data['properties']['parameter']['ALLSKY_SFC_SW_DWN']['ANN']

    solar_radiation_per_day = ann_solar_radiation 
    solar_radiation_per_year = solar_radiation_per_day * 365  # Convert to Wh/m²/year
    solar_radiation_per_year_kWh = solar_radiation_per_year / 1000  # Convert to kWh/m²/year
    solar_radiation_per_year_GWh = solar_radiation_per_year_kWh / 1_000_000  # Convert to GWh/m²/year

    # Calculate energy generated for the selected area in GWh
    energy_generated_GWh = total_area * solar_radiation_per_year_GWh
    print(energy_generated_GWh)
    
    return jsonify({
        "total_area": total_area,
        "solar_radiation_ann": solar_radiation_per_year_GWh,
        "energy_generated_GWh": energy_generated_GWh
    })

if __name__ == '__main__':
    app.run(debug=True)
