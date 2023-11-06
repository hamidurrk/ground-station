import pandas as pd
import numpy as np
from sklearn.cluster import MeanShift, estimate_bandwidth

# Read the CSV file
df = pd.read_csv('data/f_data_0.csv')  # Replace 'your_file.csv' with the actual file path

# Extract the three columns as input for clustering
X = df[['lat', 'lng', 'csq']].values

# Estimate bandwidth
bandwidth = 2

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
print(cluster_centers)
