import pandas as pd
import numpy as np
from colour import Color
from sklearn.cluster import MeanShift

def generate_color_gradient(start_color, end_color, num_steps):
    # Generate a gradient of colors from start_color to end_color
    start = Color(start_color)
    end = Color(end_color)
    gradient_colors = list(start.range_to(end, num_steps))
    
    # Convert the colors to RGB format
    rgb_colors = [(int(c.red * 255), int(c.green * 255), int(c.blue * 255)) for c in gradient_colors]
    
    return rgb_colors

# Read the CSV file
df = pd.read_csv('optimizer/final_data.csv') 

# Extract the three columns as input for clustering
X = df[['lat', 'lng', 'csq']].values

# Estimate bandwidth
bandwidth = 4

# Apply Mean Shift clustering
ms = MeanShift(bandwidth=bandwidth)
ms.fit(X)

# Retrieve cluster labels and cluster centers
labels = ms.labels_
cluster_centers = ms.cluster_centers_

# Add cluster labels to the original DataFrame
df['label'] = labels

# Save the DataFrame with cluster labels to a new CSV file
df.to_csv('optimizer/output_clusters.csv', index=False)

center_dict = {}

unique_labels = np.unique(labels)       # Get unique labels from the 'labels' array

for label in unique_labels:
    cluster_center = cluster_centers[label]     # Get the cluster center for the current label
    mean_value = cluster_center[2]              # Extract the mean value from the cluster center
    lat = cluster_center[0]                     # Extract latitude from the cluster center
    lng = cluster_center[1]                     # Extract longitude from the cluster center
    center_dict[mean_value] = (lat, lng, label) # Store information in center_dict with mean_value as key

# Sort center_dict based on mean_value (keys)
sorted_center_dict = dict(sorted(center_dict.items(), key=lambda item: item[0]))

# Generate a color gradient from "red" to "green" with the number of colors equal to the length of sorted_center_dict
colors = generate_color_gradient("red", "green", len(sorted_center_dict))

color_dict = {}     # Initialize an empty dictionary to store colors associated with mean values

for i, (key, value) in enumerate(sorted_center_dict.items()):
    color_dict[key] = [*value, colors[i]]       # Store information with mean_value as key and associated color

# Create a DataFrame from color_dict values, with columns 'lat', 'lng', 'label', 'color', and 'mean'
df = pd.DataFrame(list(color_dict.values()), columns=['lat', 'lng', 'label', 'color'])
df['mean'] = color_dict.keys()           # Add a 'mean' column with mean values as values

df.to_csv('optimizer/color_data.csv', index=False)

# Read the original data
df_data = pd.read_csv('optimizer/output_clusters.csv')  

# Read the label-color relationship data
df_labels = pd.read_csv('optimizer/color_data.csv')  

# Create a dictionary mapping labels to colors
label_color_dict = dict(zip(df_labels['label'], df_labels['color']))

# Map the colors to the labels in the original DataFrame
df_data['color'] = df_data['label'].map(label_color_dict)

# Print the updated DataFrame
df_data.to_csv('optimizer/output_clusters_color.csv', index=False)