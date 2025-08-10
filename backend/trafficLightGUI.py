import tkinter as tk
from trafficData import determine_traffic_intensities
import time
import threading
from trafficData import fetch_new_traffic_data  

class TrafficLightGUI:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, width=70, height=150)
        self.canvas.pack()
        self.colors = ["red", "yellow", "green"]
        self.current_color_index = 0
        self.draw_traffic_light()

        # Create a label for the countdown timer
        self.timer_label = tk.Label(master, text="", font=("Helvetica", 14))
        self.timer_label.pack()

    def draw_traffic_light(self):
        box_width = 50
        box_height = 175
        box_left = (70 - box_width) / 2
        box_top = (150 - box_height) / 2
        box_right = box_left + box_width
        box_bottom = box_top + box_height

        self.canvas.create_rectangle(box_left, box_top, box_right, box_bottom, fill="black")

        light_size = 20
        light_left = (70 - light_size) / 2
        light_top = box_top + 20
        light_bottom = light_top + light_size

        self.lights = [
            self.canvas.create_oval(light_left, light_top + i * (light_size + 40), light_left + light_size,
                                    light_bottom + i * (light_size + 40), fill="black")
            for i in range(3)
        ]

    def update_light(self, color, countdown_time=None):
        for light in self.lights:
            self.canvas.itemconfig(light, fill="black")
        color_index = self.colors.index(color)
        self.canvas.itemconfig(self.lights[color_index], fill=color)

        # Update the timer label if a countdown time is provided
        if countdown_time is not None:
            self.update_timer(countdown_time)
        else:
            self.timer_label.config(text="")  # Clear the timer when no countdown is needed

    def update_timer(self, time_left):
        if time_left > 0:
            self.timer_label.config(text=f"{time_left} sec")
        else:
            self.timer_label.config(text="")


def update_traffic_lights(root, road_names, snapped_points, traffic_lights, api_key, life_cycle_seconds):
    intensities = determine_traffic_intensities(snapped_points, api_key)
    sorted_indices = sorted(range(len(intensities)), key=lambda i: intensities[i], reverse=True)

    total_roads = len(road_names)
    half_cycle_time = life_cycle_seconds / 2
    secondary_cycle_time = half_cycle_time / (total_roads - 1)

    new_data_holder = []

    for index in range(len(sorted_indices)):
        current_road_index = sorted_indices[index]
        road_name = road_names[current_road_index]
        ui_label = chr(65 + current_road_index)  # Converts index to A, B, C, etc.

        for i in range(total_roads):
            if i != current_road_index:
                traffic_lights[i].update_light("red")
        root.update()

        if index == 0:
            green_time = half_cycle_time
        else:
            green_time = secondary_cycle_time

        print(f"{ui_label} ({road_name}) green for {green_time} seconds.")
        for t in range(int(green_time), 0, -1):
            traffic_lights[current_road_index].update_light("green", countdown_time=t)
            root.update()
            time.sleep(1)

        print(f"{ui_label} ({road_name}) yellow for 5 seconds.")

        if index == len(sorted_indices) - 1:
            print("Fetching new traffic data during yellow light of the last road.")
            traffic_thread = threading.Thread(target=fetch_new_traffic_data,
                                              args=(snapped_points, api_key, new_data_holder))
            traffic_thread.start()

        for t in range(5, 0, -1):
            traffic_lights[current_road_index].update_light("yellow", countdown_time=t)
            root.update()
            time.sleep(1)

        traffic_lights[current_road_index].update_light("red")
        root.update()

    if new_data_holder:
        traffic_thread.join()
        intensities = new_data_holder[0]

        print("\nNext cycle data (updated traffic intensities):")
        for i, point in enumerate(snapped_points):
            road_coords = (point['location']['latitude'], point['location']['longitude'])
            traffic_intensity = intensities[i]
            ui_label = chr(65 + i)
            print(f"{ui_label} ({road_names[i]}): Coordinates: {road_coords} | Traffic Intensity: {traffic_intensity}")

        sorted_indices = sorted(range(len(intensities)), key=lambda i: intensities[i], reverse=True)

    print("\nStarting next cycle with updated traffic data.")
    root.after(1000, update_traffic_lights, root, road_names, snapped_points, traffic_lights, api_key,
               life_cycle_seconds)

def create_traffic_lights(root, road_names, snapped_points, api_key, life_cycle_seconds):
    traffic_lights = []
    for i in range(len(road_names)):
        frame = tk.Frame(root)
        frame.pack(pady=10)

        # Use generic road labels (e.g., "Road A", "Road B", etc.)
        ui_label = chr(65 + i)  # Converts index to A, B, C, etc.
        label = tk.Label(frame, text=f"Road {ui_label}")
        label.pack()

        traffic_light = TrafficLightGUI(frame)
        traffic_lights.append(traffic_light)

    update_traffic_lights(root, road_names, snapped_points, traffic_lights, api_key, life_cycle_seconds)