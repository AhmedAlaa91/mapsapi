import pandas as pd
import os
import requests
import logging
# Load fuel price data
LOG_FILE = os.path.join(os.path.dirname(__file__), 'fuel_optimizer.log')
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
# Function to get coordinates from a city name using Nominatim
def get_coordinates(location_name):
    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search.php"
    params = {"q": location_name, "format": "jsonv2", "limit": 1}
    headers = {"User-Agent": "YourAppName/1.0 (your@email.com)"}  # Replace with your app name and contact email

    try:
        response = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data:
            return [float(data[0]["lon"]), float(data[0]["lat"])]
        logging.error(f"No coordinates found for {location_name}")
    except requests.RequestException as e:
        logging.error(f"Error fetching coordinates for {location_name}: {e}")
    return None
