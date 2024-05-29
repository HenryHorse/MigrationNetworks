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


import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import networkx as nx


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


# Load the language data with no headers and correct columns for countries and languages
language_data = pd.read_csv('language_list.txt', header=None)
language_data.columns = ['Country', 'Language1', 'Language2']

# Normalize the language names by stripping whitespace and converting to lower case
language_data['Language1'] = language_data['Language1'].str.strip().str.lower()
language_data['Language2'] = language_data['Language2'].str.strip().str.lower()

# Melt the DataFrame to have one language per row
language_data = language_data.melt(id_vars='Country', value_vars=['Language1', 'Language2'], var_name='Variable', value_name='Language')
language_data.drop(['Variable'], axis=1, inplace=True)
language_data.dropna(subset=['Language'], inplace=True)

# Load the language family data
language_families = pd.read_csv('family.txt', header=None, names=['Language', 'Family'])
language_families['Language'] = language_families['Language'].str.strip().str.lower()

# Merge the datasets on the language column to add language family
merged_data = pd.merge(language_data, language_families, on='Language', how='left')



# Merge language and family data for colonies
map_data = pd.merge(map_data, merged_data[['Country', 'Language', 'Family']], left_on='Colony', right_on='Country', how='left')
map_data.rename(columns={'Language': 'Language_Colony', 'Family': 'Family_Colony'}, inplace=True)
map_data.drop('Country', axis=1, inplace=True)  # Remove the redundant 'Country' column

# Merge language and family data for colonizers
map_data = pd.merge(map_data, merged_data[['Country', 'Language', 'Family']], left_on='Colonizer', right_on='Country', how='left')
map_data.rename(columns={'Language': 'Language_Colonizer', 'Family': 'Family_Colonizer'}, inplace=True)
map_data.drop('Country', axis=1, inplace=True)  # Remove the redundant 'Country' column

print(map_data)


# Normalize the dictionary keys
family_colors = {
    'indo-european': '#4E79A7',
    'afro-asiatic': '#F28E2B',
    'turkic': '#E15759',
    'sino-tibetan': '#59A14F',
    'austronesian': '#EDC948',
    'creole': '#B07AA1',
    'uralic': '#FF9DA7',
    'eskimo-aleut': '#9C755F',
    'tupian': '#BAB0AC',
    'japonic': '#D37295',
    'austro-asiatic': '#6C8EAD',
    'niger-congo': '#A1C181',
    'koreanic': '#E18B6B',
    'kra-dai': '#F1CE63',
    'altaic': '#76B7B2'
}

# Apply normalization when reading data or immediately after
map_data['Family_Colony'] = map_data['Family_Colony'].str.lower().str.strip()
map_data['Family_Colonizer'] = map_data['Family_Colonizer'].str.lower().str.strip()

# Now generate the map with correct color assignments
plt.figure(figsize=(15, 8))
m = Basemap(projection='merc', llcrnrlat=-60, urcrnrlat=60, llcrnrlon=-180, urcrnrlon=180, resolution='c')
m.drawcoastlines()
m.drawcountries()

# Create a directed graph
G = nx.DiGraph()

# Add nodes and edges to the graph with color properties
for _, row in map_data.iterrows():
    colonizer_color = family_colors.get(row['Family_Colonizer'].strip(), 'grey')  # Default to grey
    colony_color = family_colors.get(row['Family_Colony'].strip(), 'grey')

    # Positions
    colonizer_pos = (row['Longitude_Colonizer'], row['Latitude_Colonizer'])
    colony_pos = (row['Longitude_Colony'], row['Latitude_Colony'])

    # Adding nodes
    G.add_node(row['Colonizer'], pos=m(*colonizer_pos), color=colonizer_color, family=row['Family_Colonizer'])
    G.add_node(row['Colony'], pos=m(*colony_pos), color=colony_color, family=row['Family_Colony'])

    # Adding edge with a specific color logic
    if row['Family_Colonizer'] == row['Family_Colony']:
        edge_color = '#B2DCEF'  # Same family, highlight color
    else:
        edge_color = 'grey'  # Different family, less emphasis

    G.add_edge(row['Colonizer'], row['Colony'], color=edge_color)

# Extract node positions and colors from the graph
pos = nx.get_node_attributes(G, 'pos')
node_colors = [data['color'] for node, data in G.nodes(data=True)]

# Draw nodes
nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=50, alpha=0.8, edgecolors='black')

# Extract edge colors
edge_colors = [data['color'] for u, v, data in G.edges(data=True)]

# Draw edges
nx.draw_networkx_edges(G, pos, edgelist=G.edges(), arrows=True, arrowstyle='-|>', arrowsize=10, edge_color=edge_colors, width=1)

plt.title('Colonial Relationships and Language Families Map')
plt.show()


# Count of matching vs non-matching language families
same_family_count = map_data[map_data['Family_Colonizer'] == map_data['Family_Colony']].shape[0]
different_family_count = map_data.shape[0] - same_family_count

print(f"Same Language Family: {same_family_count}")
print(f"Different Language Family: {different_family_count}")


# Data preparation
labels = 'Same Language Family', 'Different Language Family'
sizes = [same_family_count, different_family_count]

# Plot
fig1, ax1 = plt.subplots()
ax1.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.title('Proportion of Colonial Relationships by Language Family')
plt.show()



import scipy.stats as stats


contingency_table = pd.crosstab(map_data['Colonizer'], map_data['Family_Colony'])

# Chi-Square Test
chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)


print(f"Chi-Square Statistic: {chi2}")
print(f"P-value: {p_value}")
print(f"Degrees of Freedom: {dof}")
