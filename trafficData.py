import tkinter as tk
import requests
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

def get_traffic_data(latitude, longitude, api_key, retries=3):
    for _ in range(retries):
        traffic_url = f'https://maps.googleapis.com/maps/api/distancematrix/json?origins={latitude},{longitude}&destinations={latitude + 0.001},{longitude + 0.001}&departure_time=now&traffic_model=best_guess&key={api_key}'
        response = requests.get(traffic_url)
        if response.status_code == 200:
            data = response.json()
            if 'rows' in data and 'elements' in data['rows'][0] and 'duration_in_traffic' in \
                    data['rows'][0]['elements'][0]:
                traffic_intensity = data['rows'][0]['elements'][0]['duration_in_traffic']['value']
                if traffic_intensity > 0:
                    return traffic_intensity
            else:
                print("No traffic data available for the specified location")
        time.sleep(0.1)

    print("Error fetching data from Traffic API or all attempts returned 0 traffic intensity")
    return None


def determine_traffic_intensities(snapped_points, api_key):
    intensities = []
    for point in snapped_points:
        intensity = get_traffic_data(point['location']['latitude'], point['location']['longitude'], api_key)
        intensities.append(intensity if intensity is not None else 0)
    return intensities

def fetch_new_traffic_data(snapped_points, api_key, result_holder):
    """Fetch traffic data asynchronously and store the result."""
    new_intensities = determine_traffic_intensities(snapped_points, api_key)
    result_holder.append(new_intensities)

def autofill_lat_long(selection, latitude_entry, longitude_entry):
    locations = {
        "Narengi Tinali": (26.1786, 91.8293),
        "Zoo Road Tinali": (26.1749, 91.7767),
        "Jaynagar Chariali": (26.1223, 91.8061),
        "Beltola Chariali": (26.1286, 91.8013),
        "Mission Chariali(Tezpur)": (26.6608, 92.7755),
        "Baihata Chariali": (26.3449, 91.7163),
        "Ganesguri Chariali": (26.1498, 91.7852),
        "Maligaon Chariali": (26.1592, 91.6961),
        "Basistha Chariali": (26.1113, 91.7976),
        "Thana Chariali(Dibrugarh)": (27.4810, 94.9076)
    }

    if selection in locations:
        latitude, longitude = locations[selection]
        latitude_entry.delete(0, tk.END)
        latitude_entry.insert(0, str(latitude))
        longitude_entry.delete(0, tk.END)
        longitude_entry.insert(0, str(longitude))