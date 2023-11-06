ENV = "prod"  # Set to "dev" or "prod" to change the environment

import customtkinter
from tkintermapview import TkinterMapView
from PIL import Image, ImageTk, ImageDraw
import os
import requests
import json
import time 
import random
import threading
import pandas as pd
from colour import Color
import matplotlib.pyplot as plt

# Absolute path to the directory containing this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_URL = "http://localhost:8080" if ENV == "dev" else "https://tether-s2ng.onrender.com"
 
droneLat = 23.7472533
droneLng = 90.3704085

customtkinter.set_default_color_theme("blue")


def get_gradient_color(signal_strength):
    # Define the range of signal strength values
    min_signal_strength = 0  # Worst signal strength
    max_signal_strength = 32   # Best signal strength

    # Normalize signal strength to the range [0, 1]
    normalized_signal = (signal_strength - min_signal_strength) / (max_signal_strength - min_signal_strength)

    # Create a gradient between red and green with 10 steps
    gradient_colors = list(Color("#FF3333").range_to(Color("green"), 10))

    # Calculate the index in the gradient based on the normalized signal strength
    color_index = int(normalized_signal * (len(gradient_colors) - 1))

    # Get the color from the gradient
    selected_color = gradient_colors[color_index]

    # Convert the color to RGB and add transparency
    red, green, blue = selected_color.rgb
    return int(red * 255), int(green * 255), int(blue * 255), 128  # 50% transparency
   
def create_marker_image(signal_strength):
    # Create a custom marker image using Pillow
    marker_image = Image.new("RGBA", (32, 32), (0, 0, 0, 0))  # Create a transparent image

    # Create a drawing context
    marker_draw = ImageDraw.Draw(marker_image)

    # Calculate the circle's position and size
    circle_center = (16, 16)  # Center of the image
    circle_radius = 4  # 8px diameter circle, so radius is half of that

    circle_color = get_gradient_color(signal_strength)

    # Draw a circle with gradient color
    marker_draw.ellipse(
        [circle_center[0] - circle_radius, circle_center[1] - circle_radius,
         circle_center[0] + circle_radius, circle_center[1] + circle_radius],
        fill=circle_color
    )

    # Convert the Pillow image to a PhotoImage for use in tkinter
    marker_icon = ImageTk.PhotoImage(marker_image)
    return marker_icon

def create_cluster_points(color):
    red, green, blue = color
    # Create a custom marker image using Pillow
    marker_image = Image.new("RGBA", (32, 32), (0, 0, 0, 0))  # Create a transparent image

    # Create a drawing context
    marker_draw = ImageDraw.Draw(marker_image)

    # Calculate the circle's position and size
    circle_center = (16, 16)  # Center of the image
    circle_radius = 4  # 8px diameter circle, so radius is half of that
    circle_color = int(red * 255), int(green * 255), int(blue * 255), 128
    print(circle_color)
    # Draw a circle with gradient color
    marker_draw.ellipse(
        [circle_center[0] - circle_radius, circle_center[1] - circle_radius,
         circle_center[0] + circle_radius, circle_center[1] + circle_radius],
        fill=circle_color
    )

    # Convert the Pillow image to a PhotoImage for use in tkinter
    marker_icon = ImageTk.PhotoImage(marker_image)
    return marker_icon

def load_data(csv_file):
    df = pd.read_csv(f'{csv_file}')
    return df

def put_marker(df, map_widget):
    # Place markers on the map with gradient colors
    for row in df.itertuples():
        marker_lat, marker_lng = row.lat, row.lng
        marker_icon = create_marker_image(row.csq)
        map_widget.set_marker(marker_lat, marker_lng, icon=marker_icon)
        
def generate_cluster_image(df_all, map_widget):
    for row in df_all.itertuples():
        marker_lat, marker_lng, marker_color= row.lat, row.lng, eval(row.color)
        marker_icon = create_cluster_points(marker_color)
        map_widget.set_marker(marker_lat, marker_lng, icon=marker_icon)
        


class App(customtkinter.CTk):

    APP_NAME = "Gound Station"
    WIDTH = 1400
    HEIGHT = 800


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set window properties
        self.title(App.APP_NAME)
        self.geometry(str(App.WIDTH) + "x" + str(App.HEIGHT))
        self.minsize(App.WIDTH, App.HEIGHT)
        
        

        self.marker_list = []

        # ============ create two CTkFrames ============

        self.grid_columnconfigure(0, weight=0)  # Left panel will not resize in the x direction when the screen is resized
        self.grid_columnconfigure(1, weight=1) # Right panel will resize in the x direction when the screen is resized
        self.grid_rowconfigure(0, weight=1)  # Both panels will resize in the y direction when the screen is resized

        # Left panel attach
        self.frame_left = customtkinter.CTkFrame(master=self, width=150, corner_radius=0, fg_color=None)
        self.frame_left.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        # Right panel attach
        self.frame_right = customtkinter.CTkFrame(master=self, corner_radius=0)
        self.frame_right.grid(row=0, column=1, rowspan=1, pady=0, padx=0, sticky="nsew")

        # ============ frame_left ============

        self.frame_left.grid_rowconfigure(2, weight=1)
        
        self.entrylow = customtkinter.CTkEntry(master=self.frame_left,
                                            placeholder_text="Low Val")
        self.entrylow.grid(row=0, column=0, sticky="we", pady=(20, 0), padx=(10, 10))
        
        self.entryhigh = customtkinter.CTkEntry(master=self.frame_left,
                                            placeholder_text="High Val")
        self.entryhigh.grid(row=0, column=1, sticky="we", pady=(20, 0), padx=(20, 20))
        
        # Run Plan button
        self.button_1 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Run Plan",
                                                command=self.run_plan)
        self.button_1.grid(pady=(20, 0), padx=(20, 20), row=1, column=0)

        # Clear Plan button
        self.button_2 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Clear Plan",
                                                command=self.clear_marker_event)
        self.button_2.grid(pady=(20, 0), padx=(20, 20), row=1, column=1)

        
        # View Plot button
        self.button_3 = customtkinter.CTkButton(master=self.frame_left,
                                                text="View Heatmap",
                                                command=self.view_heatmap)
        self.button_3.grid(pady=(20, 0), padx=(20, 20), row=2, column=0)
        
        self.button_3 = customtkinter.CTkButton(master=self.frame_left,
                                                text="View Cluster",
                                                command=self.view_cluster)
        self.button_3.grid(pady=(20, 0), padx=(20, 20), row=2, column=1)
        
        self.button_3 = customtkinter.CTkButton(master=self.frame_left,
                                                text="View Tower",
                                                command=self.view_optimized_towers)
        self.button_3.grid(pady=(120, 0), padx=(20, 20), row=2, column=0)
        
        # Section for selecting map type
        self.map_label = customtkinter.CTkLabel(self.frame_left, text="Tile Server:", anchor="w")
        self.map_label.grid(row=3, column=0, padx=(20, 20), pady=(20, 0))
        self.map_option_menu = customtkinter.CTkOptionMenu(self.frame_left, values=[ "Google normal", "OpenStreetMap", "Google satellite"],
                                                                       command=self.change_map)
        self.map_option_menu.grid(row=4, column=0, padx=(20, 20), pady=(10, 0))

        # Section for selecting theme
        self.appearance_mode_label = customtkinter.CTkLabel(self.frame_left, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=(20, 20), pady=(20, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.frame_left, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=(20, 20), pady=(10, 20))

        
        # ============ frame_right ============

        self.frame_right.grid_rowconfigure(1, weight=1)
        self.frame_right.grid_rowconfigure(0, weight=0)
        self.frame_right.grid_columnconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(1, weight=0)
        self.frame_right.grid_columnconfigure(2, weight=1)

        self.map_widget = TkinterMapView(self.frame_right, corner_radius=0)
        self.map_widget.grid(row=1, rowspan=1, column=0, columnspan=3, sticky="nswe", padx=(0, 0), pady=(0, 0))

        self.entry = customtkinter.CTkEntry(master=self.frame_right,
                                            placeholder_text="type address")
        self.entry.grid(row=0, column=0, sticky="we", padx=(12, 0), pady=12)
        self.entry.bind("<Return>", self.search_event)  # Run search_event() function on enter press

        self.button_5 = customtkinter.CTkButton(master=self.frame_right,
                                                text="Search",
                                                width=90,
                                                command=self.search_event)
        self.button_5.grid(row=0, column=1, sticky="w", padx=(12, 0), pady=12)

        # Add an option to add marker in the right click menu
        self.map_widget.add_right_click_menu_command(label="Add marker", command=self.add_marker, pass_coords=True)

        # Set default values
        self.map_widget.set_address("Dhaka")
        self.map_option_menu.set("Google normal") 
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.appearance_mode_optionemenu.set("Dark")
        self.droneMarker = None        

        # Load marker icons
        self.marker_icon = ImageTk.PhotoImage(Image.open(os.path.join(BASE_DIR, "images", "marker.png")).resize((40, 40)))
        # self.drone_icon = ImageTk.PhotoImage(Image.open(os.path.join(BASE_DIR, "images", "drone.png")).resize((40, 40)))

        # self.droneMarker = self.map_widget.set_marker(droneLat, droneLng, "Drone", icon=self.drone_icon)
        
    def generate_towers(self, df_towers, map_widget):
        for row in df_towers.itertuples():
            tower_lat, tower_lng= row.lat, row.lng
            self.tower_icon = ImageTk.PhotoImage(Image.open(os.path.join(BASE_DIR, "images", "network_tower.png")).resize((30, 30)))
            self.tower_marker = self.map_widget.set_marker(tower_lat, tower_lng, "____", icon=self.tower_icon)

            
    def add_marker(self, coords=None):
        marker = self.map_widget.set_marker(coords[0], coords[1], f"Point {len(self.marker_list) + 1}", icon=self.marker_icon)
        self.marker_list.append(marker)

    def search_event(self, event=None):
        self.map_widget.set_address(self.entry.get())

    def run_plan(self):
        # Accumulate the lattitude and longitude from the marker list and send it to the server
        positions = []
        low=int(self.entrylow.get())
        high=int(self.entryhigh.get())
        print(f'{low}, {high}')
        for marker in self.marker_list:
            d = {"lat": marker.position[0], "lng": marker.position[1]}
            positions.append(d)
        print(positions)
        df = pd.DataFrame(positions)
        df['csq'] = [random.randint(low, high) + 0.99 for _ in range(len(df))]
        df['lat'] = df['lat'].round(7)
        df['lng'] = df['lng'].round(7)
        df.to_csv('data/output_data.csv', index=False)
        
        # make a request to the server
        # response = requests.post(f"{SERVER_URL}/drone-control/plan", json=positions)
        # print(response.content)
        
    def clear_marker_event(self):
        for marker in self.marker_list:
            marker.delete()
        self.marker_list = []

    def change_appearance_mode(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_map(self, new_map: str):
        if new_map == "OpenStreetMap":
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif new_map == "Google normal":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        elif new_map == "Google satellite":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
    
    def view_heatmap(self):
        df = load_data('data/f_data_0.csv')
        put_marker(df, self.map_widget)
        
    def view_cluster(self):
        df_all = load_data('optimizer/output_clusters_color.csv')
        generate_cluster_image(df_all, self.map_widget)

    def view_optimized_towers(self):
        df_towers = load_data('optimizer/color_data.csv')
        self.generate_towers(df_towers, self.map_widget)
        
    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()


if __name__ == "__main__":
    app = App()
    t = threading.Thread()
    t.start()
    app.start()