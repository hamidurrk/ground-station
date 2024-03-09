
python -m venv venv




./venv/Scripts/activate




pip install -r requirements.txt


# Network Tower Location Estimation Using Mean Shift Clustering

This project aims to estimate network tower locations using the Mean Shift clustering algorithm based on signal strength measurements collected by a robot at various locations. The software provides visualization tools to analyze signal strength data and identify areas with poor network coverage.

## Overview

The ground station software processes signal strength data obtained from a robot's measurements in Dhaka, Bangladesh. The data consists of latitude, longitude, and signal strength (CSQ) values, ranging from 0 to 31. The software visualizes this data on a map, colorizing each point based on signal strength, and utilizes the Mean Shift clustering algorithm to estimate network tower locations.

## Features

- **Data Visualization**: Visualize signal strength data on a map, with color-coded markers representing signal strength levels.
- **Mean Shift Clustering**: Utilize the Mean Shift clustering algorithm to cluster data points based on signal strength measurements.
- **Cluster Analysis**: Analyze clusters to identify areas with poor network coverage and potential locations for network towers.
- **3D Plot Visualization**: Generate a 3D surface plot to visualize signal strength distribution across different locations.
- **Customizable Interface**: Customize map type and appearance mode to enhance user experience.

## Usage

1. **Data Loading**: Load signal strength data obtained from robot measurements.
2. **Data Visualization**:
   - View Heatmap: Visualize signal strength distribution on the map.
   - View Cluster: Utilize Mean Shift clustering to identify areas with poor network coverage.
   - View Tower: Visualize estimated network tower locations based on clustering results.
3. **3D Plot Visualization**: Analyze signal strength distribution using a 3D surface plot.
4. **Map Customization**: Choose map type (Google normal, Google satellite, or OpenStreetMap) and appearance mode (Light, Dark, or System).
5. **Reset**: Reset map to default settings.

## Repository Structure

- `images/`: Contains images used in the project.
- `optimizer/`: Contains scripts and data related to data optimization and clustering.
- `plots/`: Contains generated plots.
- `README.md`: Project overview and usage instructions.
- `app.py`: Main Python script for the ground station software.

## Requirements

- Python 3.x
- Tkinter
- PIL
- numpy
- matplotlib
- scipy
- pandas
- colour
- requests

## Installation

1. Clone the repository:
```
git clone https://github.com/hamidurrk/ground-station.git
```

2. Setup virtual environment:
```bash
python -m venv venv
./venv/Scripts/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```


3. Run the application:
```
python app.py
```


## Credits

This project was developed by Md Hamidur Rahman Khan as part of [Tethr]. 

