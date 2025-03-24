import tkinter as tk
import requests

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