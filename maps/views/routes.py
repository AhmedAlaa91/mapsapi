import requests
import us
import logging
import os
LOG_FILE = os.path.join(os.path.dirname(__file__), 'fuel_erouting.log')
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

#     return state_set
def get_route_states(route_data):
    state_set = set()
    state_set_abbreviation = set() 
    # Ensure routes exist
    if 'routes' not in route_data or not route_data['routes']:
        logging.error("No route data found")
        return set()
    
    route = route_data['routes'][0]

    # Extract waypoints from steps
    waypoints = []
    for segment in route.get('segments', []):
        for step in segment.get('steps', []):
            if 'way_points' in step and len(step['way_points']) == 2:
                start_idx, end_idx = step['way_points']
                waypoints.append(start_idx)  # Collect waypoint index

    if not waypoints:
        logging.error("No waypoints found in route data")
        return set()
    

    # Get bounding box (bbox) from route data
    bbox = route_data.get('bbox', [])
    if len(bbox) == 4:
        min_lon, min_lat, max_lon, max_lat = bbox
        # Divide the bounding box into smaller sections based on number of waypoints (approximation)
        # This part is a simplified method to give unique lat/lon values for each waypoint
        num_waypoints = len(waypoints)
        step_lon = (max_lon - min_lon) / num_waypoints
        step_lat = (max_lat - min_lat) / num_waypoints
        
        # Approximate the coordinates for each waypoint
        for i, waypoint_index in enumerate(waypoints):
            lon = min_lon + i * step_lon
            lat = min_lat + i * step_lat
            
            NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse.php"
            params = {
                "lat": lat,
                "lon": lon,
                "zoom": 18,
                "format": "jsonv2"
            }
            headers = {"User-Agent": "YourAppName/1.0 (your@email.com)"} 
            response = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=5)
            if response.status_code == 200 and response.json():
                address = response.json().get("address", {})
                
                # Extract the state from the response
                state = address.get("state")
                if state :
                    state_set.add(state)
                    if state == "District of Columbia" or state == "D.C.":
                        state_set_abbreviation.add('DC')
                    else :
                        state_abbr=us.states.lookup(state)
                        state_set_abbreviation.add(state_abbr.abbr)
    else:
        logging.error("Invalid bbox in route data")
        return set()

    return state_set , state_set_abbreviation
