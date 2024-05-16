# import pandas as pd

# # Load your data, ensuring all data is read as string type
# countries = pd.read_csv('country_list.txt')
# colonies = pd.read_csv('colonies_data.txt')


# # Check data types
# print(countries)
# print(colonies)

import folium
import pandas as pd

# Load your data
countries = pd.read_csv('country_list.txt', header=None, names=['Country', 'Latitude', 'Longitude', '2020 Pop', '2015 Pop', '2010 Pop', '2000 Pop', '1990 Pop'])
colonies = pd.read_csv('colonies_data.txt', header=None, names=['Colonizer', 'Colony'])

# Trim whitespace and convert to string for safe merging
countries['Country'] = countries['Country'].str.strip().astype(str)
colonies['Colony'] = colonies['Colony'].str.strip().astype(str)
colonies['Colonizer'] = colonies['Colonizer'].str.strip().astype(str)

# Merge to get coordinates for colonies
map_data = pd.merge(colonies, countries, how='left', left_on='Colony', right_on='Country')
map_data = pd.merge(map_data, countries, how='left', left_on='Colonizer', right_on='Country', suffixes=('_Colony', '_Colonizer'))

# Select only necessary columns
map_data = map_data[['Colonizer', 'Colony', 'Latitude_Colony', 'Longitude_Colony', 'Latitude_Colonizer', 'Longitude_Colonizer']]


# Drop rows where any of the latitude or longitude data is NaN
map_data = map_data.dropna(subset=['Latitude_Colonizer', 'Longitude_Colonizer', 'Latitude_Colony', 'Longitude_Colony'])
# print(map_data.isna().sum())


# import folium

# # Create a base map
# m = folium.Map(location=[0, 0], zoom_start=2)

# # Iterate through the cleaned data to add markers and lines
# for _, row in map_data.iterrows():
#     folium.Marker(
#         location=[row['Latitude_Colonizer'], row['Longitude_Colonizer']],
#         popup=f"Colonizer: {row['Colonizer']}",
#         icon=folium.Icon(color='red')
#     ).add_to(m)

#     folium.Marker(
#         location=[row['Latitude_Colony'], row['Longitude_Colony']],
#         popup=f"Colony: {row['Colony']}",
#         icon=folium.Icon(color='blue')
#     ).add_to(m)

#     folium.PolyLine(
#         locations=[
#             [row['Latitude_Colonizer'], row['Longitude_Colonizer']],
#             [row['Latitude_Colony'], row['Longitude_Colony']]
#         ],
#         color='green'
#     ).add_to(m)

# # Save or display the map
# m.save('colonial_relationships_map.html')  # Save to an HTML file


# Correct the pos dictionary setup to use the existing columns
# We will use 'Colonizer' and 'Colony' as keys and their respective coordinates for positioning


import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import networkx as nx
import pandas as pd

# Setup Basemap for plotting
plt.figure(figsize=(15, 8))
m = Basemap(projection='merc', llcrnrlat=-60, urcrnrlat=60, llcrnrlon=-180, urcrnrlon=180, resolution='c')
m.drawcoastlines()
m.drawcountries()

# Create a directed graph
G = nx.DiGraph()

# Dictionary to store positions and ensure unique nodes
unique_positions = {}

for idx, row in map_data.iterrows():
    # Add nodes if they haven't been added yet
    if row['Colonizer'] not in unique_positions:
        unique_positions[row['Colonizer']] = (m(row['Longitude_Colonizer'], row['Latitude_Colonizer']))
        G.add_node(row['Colonizer'], pos=unique_positions[row['Colonizer']])
    
    if row['Colony'] not in unique_positions:
        unique_positions[row['Colony']] = (m(row['Longitude_Colony'], row['Latitude_Colony']))
        G.add_node(row['Colony'], pos=unique_positions[row['Colony']])
    
    # Add edge
    G.add_edge(row['Colonizer'], row['Colony'], weight=1)  # Assume weight as 1 for simplicity

# Get positions from unique_positions instead of node attributes
pos = unique_positions

# Draw the nodes and edges using the positions
nx.draw_networkx_nodes(G, pos, node_size=50, node_color='blue', alpha=0.6)
# nx.draw_networkx_edges(G, pos, width=1, alpha=0.5, edge_color='green')
nx.draw_networkx_edges(G, pos, arrows=True, alpha=0.5, arrowstyle='-|>', arrowsize=10, edge_color='green', width=1)


plt.title('Colonial Relationships Map')
plt.show()
