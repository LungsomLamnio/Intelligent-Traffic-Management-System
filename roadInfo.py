from degreeChanger import meters_to_degrees_latitude
from degreeChanger import meters_to_degrees_latitude, meters_to_degrees_longitude
import requests
import time
import networkx as nx

def build_road_network(snapped_points, traffic_intensities):
    """
    Builds a graph using NetworkX with roads as edges and traffic intensities as weights.
    """
    G = nx.Graph()

    # Add nodes and edges with traffic intensity as weight
    for i in range(len(snapped_points) - 1):
        lat1, lon1 = snapped_points[i]['location']['latitude'], snapped_points[i]['location']['longitude']
        lat2, lon2 = snapped_points[i+1]['location']['latitude'], snapped_points[i+1]['location']['longitude']
        
        weight = traffic_intensities[i]  # Traffic intensity as weight

        G.add_edge((lat1, lon1), (lat2, lon2), weight=weight)

    return G

def find_most_congested_road(G):
    """
    Finds the most congested road by looking for the highest weight edge.
    """
    max_edge = max(G.edges(data=True), key=lambda x: x[2]['weight'], default=None)
    
    if max_edge:
        return max_edge[0], max_edge[1], max_edge[2]['weight']
    return None

def analyze_traffic(snapped_points, api_key):
    """
    Integrates the entire pipeline to fetch traffic data, create a graph, and find the most congested road.
    """
    # Get traffic data for snapped points
    traffic_intensities = determine_traffic_intensities(snapped_points, api_key)

    # Build road network graph
    G = build_road_network(snapped_points, traffic_intensities)

    # Find the most congested road
    congested_road = find_most_congested_road(G)
    
    if congested_road:
        (lat1, lon1), (lat2, lon2), congestion_level = congested_road
        print(f"Most congested road is between ({lat1}, {lon1}) and ({lat2}, {lon2}) with congestion level {congestion_level}")
    else:
        print("No significant congestion detected.")

    return congested_road

def get_nearest_road(latitude, longitude, api_key):
    roads_url = f'https://roads.googleapis.com/v1/nearestRoads?points={latitude},{longitude}&key={api_key}'
    response = requests.get(roads_url)
    if response.status_code == 200:
        data = response.json()
        if 'snappedPoints' in data:
            return data['snappedPoints']
        else:
            return []
    else:
        print("Error fetching data from Roads API")
        return []

    try:
        response = requests.get(roads_url, timeout=10)  # Add timeout
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()  # Process the response as needed
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def count_nearby_roads(latitude, longitude, api_key, range_m, max_snap_points=4):
    snapped_points = []
    unique_road_coords = set()

    lat_range = meters_to_degrees_latitude(range_m)
    lon_range = meters_to_degrees_longitude(range_m, latitude)

    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # Move north, east, south, west
    for dx, dy in directions:
        i = 0
        while True:
            lat = latitude + i * lat_range * dx
            lon = longitude + i * lon_range * dy
            points = get_nearest_road(lat, lon, api_key)

            for point in points:
                coords = (point['location']['latitude'], point['location']['longitude'])
                if coords not in unique_road_coords:
                    snapped_points.append(point)
                    unique_road_coords.add(coords)

                if len(snapped_points) >= max_snap_points:
                    break

            if len(snapped_points) >= max_snap_points or len(points) == 0:
                break

            i += 1
            time.sleep(0.1)
            if i > 100:  # Safeguard to prevent infinite loop in case fewer roads are available
                break

    num_roads = len(snapped_points)
    return snapped_points, num_roads

def get_nearest_major_road(latitude, longitude, api_key):
    """
    Attempt to find a nearby major road when the road is unnamed.
    """
    geocode_url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={api_key}'
    response = requests.get(geocode_url)

    if response.status_code == 200:
        data = response.json()
        if 'results' in data and data['results']:
            for result in data['results']:
                # Try to find a more detailed road name by checking address components
                for component in result['address_components']:
                    if "route" in component['types']:
                        return component['long_name']
                    # Look for sublocality, locality, etc. for hints if no road is found
                    elif "sublocality" in component['types']:
                        return f"Near {component['long_name']}"
                    elif "locality" in component['types']:
                        return f"Near {component['long_name']}"
        return "Unnamed Road (No nearby major road found)"
    else:
        return "Error retrieving road name"


def get_road_name_from_coordinates(latitude, longitude, api_key):
    """
    Retrieves the road name from coordinates using Reverse Geocoding API.
    If the road is unnamed, find the nearest major road.
    """
    geocode_url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={api_key}'
    response = requests.get(geocode_url)
    if response.status_code == 200:
        data = response.json()
        if 'results' in data and data['results']:
            # Extract the road name from the address components
            for component in data['results'][0]['address_components']:
                if "route" in component['types']:  # "route" indicates a road/street name
                    road_name = component['long_name']
                    if road_name == "Unnamed Road":
                        # If road is unnamed, try to find the nearest major road
                        return get_nearest_major_road(latitude, longitude, api_key)
                    return road_name
        return get_nearest_major_road(latitude, longitude, api_key)
    else:
        return "Error retrieving road name"


def get_road_name_or_landmark(lat, lon, api_key):
    """
    Use Google's Geocoding API to get the nearest road name.
    If the road is unnamed, find nearby landmarks or businesses and ensure names are unique.
    """
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={api_key}"
    response = requests.get(geocode_url)

    if response.status_code == 200:
        data = response.json()
        if 'results' in data and len(data['results']) > 0:
            # Check if a road name is found
            for component in data['results'][0]['address_components']:
                if "route" in component['types']:
                    road_name = component['long_name']
                    if road_name != "Unnamed Road":
                        return road_name

        # If no road name, search for nearby landmarks or businesses
        business_names = find_nearby_businesses(lat, lon, api_key)
        if business_names:
            return business_names[0]  # Return the first unique business name found
        return "No identifiable name available"
    else:
        print(f"Error fetching road name from Geocoding API: {response.status_code}")
        return "Error retrieving road name"


def find_nearby_businesses(lat, lon, api_key, radius=500):
    """
    Use Google Places API to find nearby businesses or landmarks such as schools, colleges, hotels, restaurants, gyms, car showrooms, highways, overbridges, universities, and other relevant places.
    Returns a list of business names to ensure unique road naming.
    """
    types = [
        'school', 'university', 'car_dealer', 'restaurant',
        'shopping_mall', 'hospital', 'building', 'apartment', 'bridge'
    ]
    type_str = '|'.join(types)

    places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lon}&radius={radius}&keyword={type_str}&key={api_key}"
    response = requests.get(places_url)

    if response.status_code == 200:
        data = response.json()
        if 'results' in data and len(data['results']) > 0:
            unique_businesses = set()
            for place in data['results']:
                place_types = place['types']
                if any(p_type in place_types for p_type in types):
                    unique_businesses.add(place['name'])  # Add unique names to the set
            return list(unique_businesses)  # Convert the set to a list for returning
        return []
    else:
        print(f"Error fetching nearby places from Places API: {response.status_code}")
        return []

def ensure_unique_road_name(road_name, used_names):
    """Ensure the road name is unique."""
    base_name = road_name
    counter = 1
    while road_name in used_names:
        road_name = f"{base_name} {counter}"
        counter += 1
    return road_name