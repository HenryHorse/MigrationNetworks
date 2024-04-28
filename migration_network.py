

'''
1) open the file for reading
2) put all lines into an array using readlines()
3) separate all lines by comma
4) have a list of region codes you don't want to include
5) go through the array, if either destination or origin is in the list of 
regions you don't want to include, exclude the element
6
'''

import networkx as nx
import matplotlib.pyplot as plt
import sys

MIN_EDGE_WEIGHT = 100000
BIN_SIZE = 5

f = open("undesa_pd_2020_ims_stock_by_sex_destination_and_origin.csv", "r")
csv_lines = f.readlines()
csv_lines = csv_lines[11:]
split_lines = []
for line in csv_lines:
    split_lines.append(line.split(','))
# print(split_lines[0][1]) # Destination
# print(split_lines[0][3]) # Destination Code
# print(split_lines[0][5]) # Origin
# print(split_lines[0][6]) # Origin Code
# for i in range(7, 14):
#     print(split_lines[0][i])


non_countries = ['900', '947', '1833', '921', '1832', '1830', '1835', '927', '1829', '901', '902', '934', \
                 '948', '941', '1636', '1637', '1503', '1517', '1502', '1501', '1500', '903', '910', '911', \
                    '912', '913', '914', '935', '5500', '906', '920', '5501', '922', '908', '923', '924', \
                        '925', '926', '904', '915', '916', '931', '905', '909', '927', '928', '954', '957']
countries_list = []
#print(len(split_lines))
for line in split_lines:
    if (line[3] not in non_countries and line[6] not in non_countries
        and line[3].isnumeric() and line[6].isnumeric()):
        countries_list.append(line)
# print(len(countries_list))
# print('Destination: ' + countries_list[0][1].strip() + ' ' + countries_list[0][3])
# print('Origin: ' + countries_list[0][5] + ' ' + countries_list[0][6])
# print('Number of Migrants 1990: ' + countries_list[0][7])
# Index 1 is destination name, index 3 is destination code
# Index 5 is origin name, index 6 is origin code
# Indices 7-13 are the years from 1990-2020 in increments of 5 years

G = nx.DiGraph()
year = sys.argv[1]
if (year == "1990"):
    year_index = 7 # 1990
elif (year == "1995"):
    year_index = 8 # 1995
elif (year == "2000"):
    year_index = 9 # 2000
elif (year == "2005"):
    year_index = 10 # 2005
elif (year == "2010"):
    year_index = 11 # 2010
elif (year == "2015"):
    year_index = 12 # 2015
elif (year == "2020"):
    year_index = 13 # 2020

for line in countries_list:
    dest_name = line[1].strip()
    dest_code = line[3].strip()
    origin_name = line[5].strip()
    origin_code = line[6].strip()
    string_migrants = line[year_index].strip().replace(" ", "")
    if string_migrants != '..':
        num_migrants = int(string_migrants)

        G.add_node(dest_code, name=dest_name)
        G.add_node(origin_code, name=origin_name)

        if (num_migrants > MIN_EDGE_WEIGHT):
            G.add_edge(origin_name, dest_name, weight=num_migrants)


# BETWEENNESS CENTRALITY
betweenness = nx.betweenness_centrality(G)
sorted_betweenness = sorted(betweenness.items(), key=lambda item: item[1], reverse=True)
with open("bc_out.txt", "w") as file:
    for node, bc in sorted_betweenness:
        file.write(f"{G.nodes[node]}: {bc}\n")


# CLUSTERING COEFFICIENT
clustering_directed = nx.clustering(G, weight='weight')
sorted_clustering = sorted(clustering_directed.items(), key=lambda item: item[1], reverse=True)

with open("cc_out.txt", "w") as file:
    for node, clustering in sorted_clustering:
        file.write(f"{G.nodes[node]}: {clustering}\n")

# Compute the average clustering coefficient across the entire graph
average_clustering_directed = nx.average_clustering(G, weight='weight')

#print("Directed Clustering Coefficient per Node:")
#print(clustering_directed)
print("\nAverage Directed Clustering Coefficient:")
print(average_clustering_directed)

# DEGREE DISTRIBUTION (in, out, total)

in_degrees = dict(G.in_degree())  # Returns a dictionary with node:in-degree pairs
out_degrees = dict(G.out_degree())  # Returns a dictionary with node:out-degree pairs
total_degrees = dict(G.degree())  # Returns a dictionary with node:total-degree (in + out) pairs

in_degree_values = list(in_degrees.values())
out_degree_values = list(out_degrees.values())
total_degree_values = list(total_degrees.values())


# Set up the plot with subplots
plt.figure(figsize=(14, 6))  # Wider figure to accommodate two subplots

# Plot in-degree distribution
plt.subplot(1, 2, 1)  # 1 row, 2 columns, 1st subplot
plt.hist(in_degree_values, bins=range(0, max(in_degree_values) + 2, BIN_SIZE), color='green', alpha=0.7, edgecolor='black')
plt.title('In-Degree Distribution')
plt.xlabel('In-Degree')
plt.ylabel('Frequency')
plt.grid(True, which='both', linestyle='--', linewidth=0.5)

# Plot out-degree distribution
plt.subplot(1, 2, 2)  # 1 row, 2 columns, 2nd subplot
plt.hist(out_degree_values, bins=range(0, max(out_degree_values) + 2, BIN_SIZE), color='red', alpha=0.7, edgecolor='black')
plt.title('Out-Degree Distribution')
plt.xlabel('Out-Degree')
plt.ylabel('Frequency')
plt.grid(True, which='both', linestyle='--', linewidth=0.5)

plt.tight_layout()  # Adjusts subplots to fit into figure area.
plt.show()


# Choose a layout that provides better spacing, and adjust parameters if necessary
pos = nx.spring_layout(G, scale=20)  # You can increase the scale to spread out nodes
plt.figure(figsize=(15, 15))  # Large figure size to accommodate the graph
# Nodes
node_size = max(100, 7000 / len(G.nodes()))  # Avoid too large node sizes for large graphs
nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color='skyblue', alpha=0.6)
# Edges
edge_widths = [0.005 * G[u][v]['weight'] for u, v in G.edges()]  # Scale down edge widths if they are too large
nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.5, edge_color='black')
# Labels
font_size = max(8, 100 / len(G.nodes())**0.5)  # Smaller font size for larger graphs
nx.draw_networkx_labels(G, pos, font_size=font_size, font_family='sans-serif')

plt.axis('off')  # Turn off the axis
plt.title('Network of Migration (' + sys.argv[1] + ')')
plt.show()

