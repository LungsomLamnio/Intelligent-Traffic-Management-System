import tkinter as tk
import requests
import networkx as nx
import matplotlib.pyplot as plt
plt.switch_backend('TkAgg')
from roadInfo import get_nearest_road, count_nearby_roads

def analyze_traffic(snapped_points, api_key):
    """
    Build and analyze a road network graph based on snapped points and traffic intensity.
    """
    G = nx.Graph()
    
    for point in snapped_points:
        lat, lon = point['location']['latitude'], point['location']['longitude']
        road_name = point.get('roadName', f"Road ({lat}, {lon})")  # Assign a road name if available
        
        G.add_node(road_name, latitude=lat, longitude=lon)
    
    # Add edges between consecutive points to represent connectivity
    for i in range(len(snapped_points) - 1):
        point1 = snapped_points[i]
        point2 = snapped_points[i + 1]
        
        lat1, lon1 = point1['location']['latitude'], point1['location']['longitude']
        lat2, lon2 = point2['location']['latitude'], point2['location']['longitude']
        
        road1 = point1.get('roadName', f"Road ({lat1}, {lon1})")
        road2 = point2.get('roadName', f"Road ({lat2}, {lon2})")
        
        # Assume weight as 1 (distance-based weights can be added later)
        G.add_edge(road1, road2, weight=1)

    return G


def visualize_graph(G):
    """
    Visualize the road network graph.
    """
    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G)  # Layout for better visualization
    nx.draw(G, pos, with_labels=True, node_size=3000, node_color="lightblue", font_size=8, edge_color="gray")
    plt.title("Road Network Graph")
    plt.show()


# Example Usage:
if __name__ == "__main__":
    api_key = "YOUR_GOOGLE_API_KEY"
    latitude = 26.1786  # Example latitude
    longitude = 91.8293  # Example longitude
    range_m = 100  # Search radius in meters

    # Get snapped road points
    snapped_points, _ = count_nearby_roads(latitude, longitude, api_key, range_m)

    # Analyze traffic and build graph
    G = analyze_traffic(snapped_points, api_key)

    # Visualize the graph
    visualize_graph(G)

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