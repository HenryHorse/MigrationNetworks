

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
year_index = 7 # 1990
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

        G.add_edge(origin_code, dest_code, weight=num_migrants)


# BETWEENNESS CENTRALITY
betweenness = nx.betweenness_centrality(G)
sorted_betweenness = sorted(betweenness.items(), key=lambda item: item[1], reverse=True)
with open("bc_out.txt", "w") as file:
    for node, bc in sorted_betweenness:
        file.write(f"{G.nodes[node]['name']}: {bc}\n")


# CLUSTERING COEFFICIENT
clustering_directed = nx.clustering(G, weight='weight')
sorted_clustering = sorted(clustering_directed.items(), key=lambda item: item[1], reverse=True)

with open("cc_out.txt", "w") as file:
    for node, clustering in sorted_clustering:
        file.write(f"{G.nodes[node]['name']}: {clustering}\n")

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

# Plot total degree distribution
plt.subplot(133)  # 1 row, 3 columns, 3rd subplot
plt.hist(total_degree_values, bins=range(max(total_degree_values)+1), color='red', alpha=0.7)
plt.title('Total Degree Distribution')
plt.xlabel('Degree')
plt.ylabel('Frequency')

plt.tight_layout()
plt.show()




# Choose a layout that provides better spacing, and adjust parameters if necessary
pos = nx.spring_layout(G, scale=2)  # You can increase the scale to spread out nodes
plt.figure(figsize=(15, 15))  # Large figure size to accommodate the graph
# Nodes
node_size = max(100, 7000 / len(G.nodes()))  # Avoid too large node sizes for large graphs
nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color='skyblue', alpha=0.6)
# Edges
edge_widths = [0.005 * G[u][v]['weight'] for u, v in G.edges()]  # Scale down edge widths if they are too large
nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.5, edge_color='gray')
# Labels
font_size = max(8, 100 / len(G.nodes())**0.5)  # Smaller font size for larger graphs
nx.draw_networkx_labels(G, pos, font_size=font_size, font_family='sans-serif')

plt.axis('off')  # Turn off the axis
plt.title('Network of Migration (1990)')
plt.show()

