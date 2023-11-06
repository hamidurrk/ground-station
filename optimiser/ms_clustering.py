import pandas as pd
import numpy as np
from colour import Color
from sklearn.cluster import MeanShift, estimate_bandwidth

def generate_color_gradient(start_color, end_color, num_steps):
    # Generate a gradient of colors from start_color to end_color
    start = Color(start_color)
    end = Color(end_color)
    gradient_colors = list(start.range_to(end, num_steps))
    
    # Convert the colors to RGB format
    rgb_colors = [(int(c.red * 255), int(c.green * 255), int(c.blue * 255)) for c in gradient_colors]
    
    return rgb_colors

# Read the CSV file
df = pd.read_csv('data/f_data_0.csv')  # Replace 'your_file.csv' with the actual file path

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
df['Cluster'] = labels

# Save the DataFrame with cluster labels to a new CSV file
df.to_csv('optimiser/output_clusters.csv', index=False)

# Print the results
print(f'Number of clusters: {len(np.unique(labels))}')
print('Cluster centers:')

center_dict = {row[2]: row[:2] for row in cluster_centers}
print(center_dict)

sorted_center_dict = dict(sorted(center_dict.items(), key=lambda item: item[0]))
print(sorted_center_dict)

colors = generate_color_gradient("red", "green", len(sorted_center_dict))

color_dict = {}

for i, (key, value) in enumerate(sorted_center_dict.items()):
    color_dict[key] = [*value, colors[i]]

print(color_dict)

df = pd.DataFrame(list(color_dict.values()), columns=['lat', 'lng', 'color'])
df['mean'] = color_dict.keys()
df.to_csv('optimiser/color_data.csv', index=False)
