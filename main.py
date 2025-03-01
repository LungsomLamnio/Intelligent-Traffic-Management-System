import os
import time
import requests
import tkinter as tk
from config import API_KEY, API_KEY2
from trafficData import fetch_new_traffic_data, autofill_lat_long
from roadInfo import get_road_name_from_coordinates, count_nearby_roads
from degreeChanger import meters_to_degrees_latitude, meters_to_degrees_longitude
from submit import submit

#this is main file

def main():
    window = tk.Tk()
    window.title("Traffic Management System with Google Maps Circle")

    # Create the input fields
    tk.Label(window, text="Latitude:").grid(row=0, column=0)
    latitude_entry = tk.Entry(window)
    latitude_entry.grid(row=0, column=1)

    tk.Label(window, text="Longitude:").grid(row=1, column=0)
    longitude_entry = tk.Entry(window)
    longitude_entry.grid(row=1, column=1)

    tk.Label(window, text="Traffic Box ID:").grid(row=2, column=0)
    box_id_entry = tk.Entry(window)
    box_id_entry.grid(row=2, column=1)

    tk.Label(window, text="Range (meters):").grid(row=3, column=0)
    range_entry = tk.Entry(window)
    range_entry.grid(row=3, column=1)

    tk.Label(window, text="Life Cycle (seconds):").grid(row=4, column=0)
    life_cycle_entry = tk.Entry(window)
    life_cycle_entry.grid(row=4, column=1)

    tk.Label(window, text="Max Snap Points:").grid(row=5, column=0)
    max_snap_points_entry = tk.Entry(window)
    max_snap_points_entry.grid(row=5, column=1)

    # Add location recommendation dropdown
    tk.Label(window, text="Choose Location:").grid(row=6, column=0)
    location_options = [
        "Narengi Tinali", "Zoo Road Tinali", "Jaynagar Chariali", "Beltola Chariali",
        "Mission Chariali(Tezpur)", "Baihata Chariali", "Ganesguri Chariali",
        "Maligaon Chariali", "Basistha Chariali", "Thana Chariali(Dibrugarh)"
    ]
    location_var = tk.StringVar(window)
    location_var.set("Select a location")

    location_menu = tk.OptionMenu(window, location_var, *location_options,
                                  command=lambda selection: autofill_lat_long(selection, latitude_entry,
                                                                              longitude_entry))
    location_menu.grid(row=6, column=1)

    # Submit button to trigger the map update
    submit_button = tk.Button(window, text="Submit",
                              command=lambda: submit(latitude_entry, longitude_entry, box_id_entry, range_entry, life_cycle_entry, max_snap_points_entry))
    submit_button.grid(row=7, column=1)

    window.mainloop()


if __name__ == "__main__":
    main()