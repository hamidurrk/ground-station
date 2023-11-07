import customtkinter
from tkintermapview import TkinterMapView
from PIL import Image, ImageTk, ImageDraw
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from scipy.interpolate import griddata
import csv
import os
import requests
import json
import time 
import random
import threading
import pandas as pd
from colour import Color
import subprocess

# Absolute path to the directory containing this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
    # Draw a circle with color
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
    # Place towers on the map 
    for row in df_all.itertuples():
        marker_lat, marker_lng, marker_color= row.lat, row.lng, eval(row.color)
        marker_icon = create_cluster_points(marker_color)
        map_widget.set_marker(marker_lat, marker_lng, icon=marker_icon)

def filter():
    df = pd.read_csv('optimizer/final_data.csv')
    df = df.dropna()            # Remove rows with missing values
    df['csq'] = df['csq'].str.replace('"', '').str.replace(',', '.').astype(float)      # Clean "" and convert 'csq' column to float
    df = df.drop_duplicates(subset=['lat', 'lng'])          # Remove duplicate rows based on 'lat' and 'lng'
    df.to_csv('optimizer/final_data.csv', index=False)      # Save the filtered data back to the original one
    
class App(customtkinter.CTk):

    APP_NAME = "Gound Station"
    WIDTH = 1400
    HEIGHT = 800
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set window properties
        INITIAL_WIDTH = self.winfo_screenwidth()
        INITIAL_HEIGHT = self.winfo_screenheight()
        self.title(App.APP_NAME)
        self.geometry(str(INITIAL_WIDTH) + "x" + str(INITIAL_HEIGHT) + "+0+0")
        self.minsize(App.WIDTH, App.HEIGHT)
        
        self.marker_list = []

        # ============ create two CTkFrames ============

        self.grid_columnconfigure(0, weight=0)  # Left panel will not resize in the x direction when the screen is resized
        self.grid_columnconfigure(1, weight=1) # Right panel will resize in the x direction when the screen is resized
        self.grid_rowconfigure(0, weight=1)  # Both panels will resize in the y direction when the screen is resized

        # Left panel attach
        self.frame_left = customtkinter.CTkFrame(master=self, width=100, corner_radius=0, fg_color=None)
        self.frame_left.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        # Right panel attach
        self.frame_right = customtkinter.CTkTabview(master=self, corner_radius=10)
        self.frame_right.grid(row=0, column=1, rowspan=1, pady=0, padx=0, sticky="nsew")
        

        # ============ frame_left ============

        self.frame_left.grid_rowconfigure(25, weight=1)
        
                # ============ frame_left optimizer ============
        self.logo_label = customtkinter.CTkLabel(self.frame_left, text="Ground Station", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.subframe_optimizer = customtkinter.CTkFrame(master=self.frame_left)
        self.subframe_optimizer.grid(row=1, column=0, padx=(20, 20), pady=(20, 0), sticky="nsew", rowspan=5)
        self.subframe_optimizer_label = customtkinter.CTkLabel(master=self.subframe_optimizer, text="Optimizer Functions")
        self.subframe_optimizer_label.grid(row=1, column=0, columnspan=1, padx=10, pady=10, sticky="")
        
        # Start process button
        self.button_1 = customtkinter.CTkButton(master=self.subframe_optimizer,
                                                text="Start Loading Data",
                                                command=self.raw_load)
        self.button_1.grid(pady=(0, 0), padx=(20, 20), row=2, column=0)
        
        # View Heatmap button
        self.button_2 = customtkinter.CTkButton(master=self.subframe_optimizer, state="disabled",
                                                text="View Heatmap",
                                                command=self.view_heatmap)
        self.button_2.grid(pady=(20, 0), padx=(20, 20), row=3, column=0)
        
        # View Cluster button
        self.button_3 = customtkinter.CTkButton(master=self.subframe_optimizer, state="disabled",
                                                text="View Cluster",
                                                command=self.view_cluster)
        self.button_3.grid(pady=(20, 0), padx=(20, 20), row=4, column=0)
        
        # View Tower button
        self.button_4 = customtkinter.CTkButton(master=self.subframe_optimizer, state="disabled",
                                                text="View Tower",
                                                command=self.view_optimized_towers)
        self.button_4.grid(pady=(20, 20), padx=(20, 20), row=5, column=0)

                # ============ frame_left misc. ============
        # Section for selecting map type
        self.map_label = customtkinter.CTkLabel(self.frame_left, text="Tile Server:", anchor="w")
        self.map_label.grid(row=22, column=0, padx=(20, 20), pady=(20, 0))
        self.map_option_menu = customtkinter.CTkOptionMenu(self.frame_left, values=[ "Google normal", "OpenStreetMap", "Google satellite"],
                                                                       command=self.change_map)
        self.map_option_menu.grid(row=23, column=0, padx=(20, 20), pady=(10, 0))

        # Section for selecting theme
        self.appearance_mode_label = customtkinter.CTkLabel(self.frame_left, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=25, column=0, padx=(20, 20), pady=(20, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.frame_left, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode)
        self.appearance_mode_optionemenu.grid(row=25, column=0, padx=(20, 20), pady=(100, 20))

        # ============ frame_right ============
        
        self.frame_right.add("Map")  
        self.frame_right.add("Plot")
        
        # Map tab
        self.frame_right.tab("Map").grid_rowconfigure(1, weight=1)
        self.frame_right.tab("Map").grid_rowconfigure(0, weight=0)
        self.frame_right.tab("Map").grid_columnconfigure(0, weight=1)
        self.frame_right.tab("Map").grid_columnconfigure(1, weight=0)
        self.frame_right.tab("Map").grid_columnconfigure(2, weight=1)
        
        # Plot tab
        self.frame_right.tab("Plot").grid_rowconfigure(1, weight=1)
        self.frame_right.tab("Plot").grid_rowconfigure(0, weight=0)
        self.frame_right.tab("Plot").grid_columnconfigure(0, weight=1)
        self.frame_right.tab("Plot").grid_columnconfigure(1, weight=0)
        self.frame_right.tab("Plot").grid_columnconfigure(2, weight=1)
        
        # Map widget
        self.map_widget = TkinterMapView(self.frame_right.tab("Map"), corner_radius=0)
        self.map_widget.grid(row=1, rowspan=1, column=0, columnspan=3, sticky="nswe", padx=(0, 0), pady=(0, 0))

        # Entry field and button
        self.entry = customtkinter.CTkEntry(master=self.frame_right.tab("Map"),
                                            placeholder_text="type address")
        self.entry.grid(row=0, column=0, sticky="we", padx=(12, 0), pady=12)
        self.entry.bind("<Return>", self.search_event)          # Run search_event() function on enter press

        self.search = customtkinter.CTkButton(master=self.frame_right.tab("Map"),
                                                text="Search",
                                                width=90,
                                                command=self.search_event)
        self.search.grid(row=0, column=1, sticky="w", padx=(12, 0), pady=12)
        
        # Reset button
        self.button_reset = customtkinter.CTkButton(master=self.frame_right.tab("Map"),
                                                text="Reset Map",
                                                command=self.reset)
        self.button_reset.grid(pady=(0, 0), padx=(20, 20), row=0, column=2, sticky="e")

        # Set default values
        self.map_widget.set_address("Dhaka")
        self.map_option_menu.set("Google normal") 
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.appearance_mode_optionemenu.set("Dark")

        
    def generate_towers(self, df_towers, map_widget):
        # Iterate over rows in the DataFrame 'df_towers'
        for row in df_towers.itertuples():
            tower_lat, tower_lng= row.lat, row.lng
            
            # Load and resize the network tower icon
            self.tower_icon = ImageTk.PhotoImage(Image.open(os.path.join(BASE_DIR, "images", "network_tower.png")).resize((30, 30)))
            
            # Set a tower marker on the map widget at the specified latitude and longitude with a custom icon
            self.tower_marker = self.map_widget.set_marker(tower_lat, tower_lng, "____", icon=self.tower_icon)
    
    # Search bar
    def search_event(self, event=None):
        self.map_widget.set_address(self.entry.get())
    
    def plot_data(self):
        x = []
        y = []
        signal_strength = []

         # Open and read the CSV file 'final_data.csv'
        with open('optimizer/final_data.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader)        # Skip the header row 
            for row in reader:
                x.append(float(row[0]))     # Append the first column (latitude) as float to x
                y.append(float(row[1]))     # Append the second column (longitude) as float to y
                signal_strength.append(float(row[2]))       # Append the third column (csq) as float to signal_strength
        
        # Convert x to a NumPy array for plotting
        x = np.array(x)
        y = np.array(y)
        signal_strength = np.array(signal_strength)

        # Create a 2D grid of x and y values
        grid_x, grid_y = np.mgrid[min(x):max(x):100j, min(y):max(y):100j]

        # Interpolate signal strength values on the grid using cubic interpolation
        grid_z = griddata((x, y), signal_strength, (grid_x, grid_y), method='cubic')
        
        # Create a 3D plot
        plt.figure(figsize=(10, 8))
        ax = plt.axes(projection='3d')
        ax.plot_surface(grid_x, grid_y, grid_z, cmap='plasma')      # Plot the surface using 'plasma' colormap
        plt.savefig('plots/plot.png', dpi=300, bbox_inches='tight')     # Save the plot as 'plot.png'
        plot_image = customtkinter.CTkImage(Image.open("plots/plot.png"), size=(800, 800))      # Open the saved plot image and set size
        image = customtkinter.CTkLabel(self.frame_right.tab("Plot"), image=plot_image, text="")     # Create a labeled image widget
        image.grid(row=0, column=0)         # Place the image widget in the specified row and column
        
    def view_plt(self):
        x = []
        y = []
        signal_strength = []

        # Open and read the CSV file 'final_data.csv'
        with open('optimizer/final_data.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader)        # Skip the header row 
            for row in reader:
                x.append(float(row[0]))     # Append the first column (latitude) as float to x
                y.append(float(row[1]))     # Append the second column (longitude) as float to y
                signal_strength.append(float(row[2]))       # Append the third column (csq) as float to signal_strength
        
        # Convert x to a NumPy array for plotting
        x = np.array(x)
        y = np.array(y)
        signal_strength = np.array(signal_strength)

        # Create a 2D grid of x and y values
        grid_x, grid_y = np.mgrid[min(x):max(x):100j, min(y):max(y):100j]

        # Interpolate signal strength values on the grid using cubic interpolation
        grid_z = griddata((x, y), signal_strength, (grid_x, grid_y), method='cubic')
        
        # Create a 3D plot
        plt.figure(figsize=(10, 8))
        ax = plt.axes(projection='3d')
        ax.plot_surface(grid_x, grid_y, grid_z, cmap='plasma')      # Plot the surface using 'plasma' colormap
        plt.show()      # Display the plot
        
    def raw_load(self):
        target_location = os.path.join(BASE_DIR, "raw")     # Define the target directory path
        if os.path.exists(target_location):
            contents = os.listdir(target_location)
            merged_data = pd.DataFrame()
            dataframes = []     # Initialize an empty list to store DataFrames
            
            # Iterate over files in the directory
            for file_name in contents:
                print(file_name)
                file_path = os.path.join(target_location, file_name)
                df = pd.read_csv(file_path)
                dataframes.append(df)           # Append the DataFrame to the list   
                    
            merged_data = pd.concat(dataframes, ignore_index=True)      # Concatenate all DataFrames into one
            output_file = os.path.join(BASE_DIR, 'optimizer', 'final_data.csv')
            merged_data.to_csv(output_file, index=False, header=['lat', 'lng', 'csq'])
            
            filter()        # Filter the data
            
            # Enable other 3 buttons
            self.button_2.configure(state="normal")
            self.button_3.configure(state="normal")
            self.button_4.configure(state="normal")
        else:
            print(f"The location {target_location} does not exist.")
            
    def change_appearance_mode(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_map(self, new_map: str):
        # Set the tile server URL for three maps
        if new_map == "OpenStreetMap":          
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif new_map == "Google normal":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        elif new_map == "Google satellite":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
    
    def reset(self):
        # Upon reset, reboot tile server and destry all markers
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.map_widget.delete_all_marker() 
    
    def view_heatmap(self):
        df = load_data('optimizer/final_data.csv')
        put_marker(df, self.map_widget)
        
    def view_cluster(self):
        file_path = os.path.join(BASE_DIR, 'optimizer', 'ms_clustering.py')         
        subprocess.run(['python', file_path])           # Run the mean shift algorithm script using subprocess
        df_all = load_data('optimizer/output_clusters_color.csv')
        generate_cluster_image(df_all, self.map_widget)     # Generate cluster images on the map widget
        
        # Call the plot function
        self.plot_data()
        
        # Create a button for showing the 3D plot
        self.threed_plot = customtkinter.CTkButton(master=self.frame_right.tab("Plot"),
                                                text="Show 3D Plot",
                                                command=self.view_plt)
        self.threed_plot.grid(pady=(0, 0), padx=(20, 20), row=0, column=1, sticky="ne")

    def view_optimized_towers(self):
        df_towers = load_data('optimizer/color_data.csv')
        self.generate_towers(df_towers, self.map_widget)        # Generate towers on the map widget
        
    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()


if __name__ == "__main__":
    app = App()
    t = threading.Thread()
    t.start()
    app.start()