import pandas as pd
from django.http import JsonResponse
from django.views import View
from django.shortcuts import render
import os
import requests
from .coordinates2Name import get_coordinates
from .fuelData import load_fuel_data
from .routes import get_route_states
import logging
VEHICLE_RANGE = 500  # miles
FUEL_EFFICIENCY = 10  # miles per gallon
LOG_FILE = os.path.join(os.path.dirname(__file__), 'fuel_optimizer.log')
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
class OptimizeFuelRoute(View):
    def get(self, request):
        start_location = request.GET.get('start')
        end_location = request.GET.get('end')
        
        if not start_location or not end_location:
            return JsonResponse({'error': 'Missing start or end location'}, status=400)
        
        start_coords = get_coordinates(start_location)
        end_coords = get_coordinates(end_location)
        
        if not start_coords or not end_coords:
            return JsonResponse({'error': 'Invalid start or end location'}, status=400)
        
        fuel_data = load_fuel_data()
        
        # Use OpenRouteService for route calculation
        ORS_API_KEY = '5b3ce3597851110001cf62482290f893060345c0b85a66e34bb83a18'
        ORS_URL = 'https://api.openrouteservice.org/v2/directions/driving-car'
        headers = {'Authorization': ORS_API_KEY, 'Content-Type': 'application/json'}
        data = {"coordinates": [start_coords, end_coords], "format": "json"}
        
        response = requests.post(ORS_URL, json=data, headers=headers)
        if response.status_code != 200:
            return JsonResponse({'error': 'Failed to fetch route data'}, status=500)
        
        route_data = response.json()
    
        route_states_names ,   route_states= get_route_states(route_data)
        
        # Filter fuel stations by route states
        filtered_fuel_data = [stop for stop in fuel_data if stop['State'] in route_states]

        

        
        stops = []
        total_cost = 0
        remaining_range = VEHICLE_RANGE
        distance_covered = 0


        
        for segment in route_data['routes'][0]['segments']:
            segment_distance = segment['distance'] / 1609.34  # Convert to miles
            distance_covered += segment_distance
            remaining_range -= segment_distance
       
            if remaining_range <= 0:
                affordable_stops = [stop for stop in filtered_fuel_data if distance_covered - VEHICLE_RANGE <= stop.get('distance', distance_covered)]
        
                if affordable_stops:
                    best_stop = min(affordable_stops, key=lambda x: x['Retail Price'])
                    stops.append(best_stop)
                    total_cost += (VEHICLE_RANGE / FUEL_EFFICIENCY) * best_stop['Retail Price']
                    remaining_range = VEHICLE_RANGE  # Refuel
        
        return JsonResponse({
            'route': route_data['routes'][0],
            'total_distance':segment_distance,
            'route_states_names': list(route_states_names),
            'route_states': list(route_states),
            'fuel_stops': stops,
            'total_fuel_cost': total_cost,
            'total_stops': len(stops)
        })