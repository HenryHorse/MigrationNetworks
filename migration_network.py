import matplotlib
matplotlib.use('TkAgg')
import networkx as nx
import matplotlib.pyplot as plt
import sys
from mpl_toolkits.basemap import Basemap

MIN_EDGE_WEIGHT = 100000
BIN_SIZE = 5

def main():
    f = open("undesa_pd_2020_ims_stock_by_sex_destination_and_origin.csv", "r")
    csv_lines = f.readlines()
    csv_lines = csv_lines[11:]
    split_lines = []
    for line in csv_lines:
        split_lines.append(line.split(','))

    non_countries = ['900', '947', '1833', '921', '1832', '1830', '1835', '927', '1829', '901', '902', '934', \
                    '948', '941', '1636', '1637', '1503', '1517', '1502', '1501', '1500', '903', '910', '911', \
                        '912', '913', '914', '935', '5500', '906', '920', '5501', '922', '908', '923', '924', \
                            '925', '926', '904', '915', '916', '931', '905', '909', '927', '928', '954', '957']
    countries_list = []
    for line in split_lines:
        if (line[3] not in non_countries and line[6] not in non_countries
            and line[3].isnumeric() and line[6].isnumeric()):
            countries_list.append(line)

    # get year and politics indices
    year_index = get_year_index()
    politics_index = get_politics_index()

    # create graph and get data
    G = nx.DiGraph()
    data = get_data(G, countries_list, year_index, politics_index)
    
    # BETWEENNESS CENTRALITY
    betweenness_centrality(G)

    # CLUSTERING COEFFICIENT
    clustering_coefficient(G)

    # Compute the average clustering coefficient across the entire graph
    average_clustering_directed = nx.average_clustering(G, weight='weight')
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

    # Show plot
    plt.tight_layout()  # Adjusts subplots to fit into figure area.
    plt.show()

    # Get latitudes and longitudes
    countries = {}
    with open("country_list.txt", "r") as file:
        for line in file:
            parts = line.strip().split(",")
            country_name = parts[0]
            lat = float(parts[1])
            lon = float(parts[2])
            countries[country_name] = (lat, lon)

    # Draw map
    plt.figure(figsize=(14, 8))  # Set the size of the map
    m = Basemap(projection='merc', llcrnrlat=-60, urcrnrlat=70, llcrnrlon=-180, urcrnrlon=180, lat_ts=20, resolution='c')
    m.drawcoastlines()
    m.drawcountries()

    # Remove certain nodes
    pos = {}
    removed_nodes = []
    for node in G.nodes(data=True):
        country = node[1]['name']
        if country in countries:
            lat, lon = countries[country]
            pos[node[0]] = m(lon, lat)  # Map projection coordinates
        else:
            print(f"Warning: No coordinates found for {country}")
            removed_nodes.append(node[0])
    for node in removed_nodes:
        G.remove_node(node)

    # Draw nodes with geographical positions
    nx.draw_networkx_nodes(G, pos, node_size=20, node_color='blue', alpha=0.6, ax=plt.gca())


    # Draw edges with geographical positions
    for c1, c2, cdata in G.edges(data=True):
        origin_name = G.nodes[c1]['name']
        dest_name = G.nodes[c2]['name']
        edge_widths = [0.0000005 * G[c1][c2]['weight']]
        edge_color = 'black'  # Default color for no democracy index data

        origin_dem = G.nodes[c1]['dem_index']
        dest_dem = G.nodes[c2]['dem_index']

        if origin_dem != -1 and dest_dem != -1:
            if dest_dem > origin_dem:
                edge_color = 'blue'
            elif dest_dem < origin_dem:
                edge_color = 'red'

        nx.draw_networkx_edges(G, pos, edgelist=[(c1, c2)], edge_color=edge_color, width=edge_widths)

    # Show map
    plt.title('Global Migration Network')
    plt.show()

    # Choose a layout that provides better spacing, and adjust parameters if necessary
    pos = nx.spring_layout(G, scale=20)  # You can increase the scale to spread out nodes
    plt.figure(figsize=(15, 15))  # Large figure size to accommodate the graph
    # Nodes
    node_size = max(100, 7000 / len(G.nodes()))  # Avoid too large node sizes for large graphs
    nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color='skyblue', alpha=0.6)
    # Edges
    edge_widths = [0.0000005 * G[u][v]['weight'] for u, v in G.edges()]  # Scale down edge widths if they are too large
    nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.5, edge_color='black')
    # Labels
    font_size = max(8, 100 / len(G.nodes())**0.5)  # Smaller font size for larger graphs
    nx.draw_networkx_labels(G, pos, font_size=font_size, font_family='sans-serif')

    plt.axis('off')  # Turn off the axis
    plt.title('Network of Migration (' + sys.argv[1] + ')')
    plt.show()

    # Get average change in democracy
    total_migrants = 0
    total_change = 0
    emigrated_dem_index = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    immigrated_dem_index = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for element in data:        
        if (element["origin_dem"] != -1 and element["dest_dem"] != -1):
            total_migrants += element["migrants"]
            total_change += element["migrants"] * (element["dest_dem"] - element["origin_dem"])
            immigrated_dem_index[int(element["dest_dem"])] += total_migrants
            emigrated_dem_index[int(element["origin_dem"])] += total_migrants
    average_change = total_change / total_migrants
    print("Average change in democracy index: " + str(average_change))

    # "Is the a specific level of democracy people tend to migrate from or to?"
    # Set up the plot with subplots
    plt.figure(figsize=(14, 6))  # Wider figure to accommodate two subplots

    # Plot in-degree distribution
    plt.subplot(1, 2, 1)  # 1 row, 2 columns, 1st subplot
    plt.bar([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], emigrated_dem_index, color='green', alpha=0.7, edgecolor='black')
    plt.title('Democracy Index of countries emigrated from')
    plt.xlabel('Democracy Index')
    plt.ylabel('Emigrants')
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Plot out-degree distribution
    plt.subplot(1, 2, 2)  # 1 row, 2 columns, 2nd subplot
    plt.bar([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], immigrated_dem_index, color='red', alpha=0.7, edgecolor='black')
    plt.title('Democracy Index of countries immigrated to')
    plt.xlabel('Democracy Index')
    plt.ylabel('Immigrants')
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Show plot
    plt.tight_layout()  # Adjusts subplots to fit into figure area.
    plt.show()

def get_year_index():
    year = sys.argv[1]
    if (year == "1990"):
        return 7
    elif (year == "1995"):
        return 8
    elif (year == "2000"):
        return 9
    elif (year == "2005"):
        return 10
    elif (year == "2010"):
        return 11
    elif (year == "2015"):
        return 12
    elif (year == "2020"):
        return 13
    
def get_politics_index():
    year = sys.argv[1]
    if (year == "2020"):
        return 1
    elif (year == "2015"):
        return 2
    elif (year == "2010"):
        return 3
    else:
        return -1
    
def get_data(G, countries_list, year_index, politics_index):
    politics = []
    f_politics = open("Economist_Democracy_Index_CSV.csv", "r")
    csv_lines = f_politics.readlines()
    csv_lines = csv_lines[1:]
    for line in csv_lines:
        politics.append(line.split(','))

    data = [] # dataset containing all migration flows
    for line in countries_list:
        origin_name = line[5].strip()
        origin_code = line[6].strip()
        dest_name = line[1].strip()
        dest_code = line[3].strip()
        string_migrants = line[year_index].strip().replace(" ", "")
        if string_migrants != '..':
            num_migrants = int(string_migrants)
            origin_dem = -1
            dest_dem = -1
            if (politics_index >= 0):
                for country in politics:
                    if country[0].strip() == origin_name:
                        origin_dem = float(country[politics_index].strip())
                    elif country[0].strip() == dest_name:
                        dest_dem = float(country[politics_index].strip())
            data.append({"dest_name": dest_name,
                        "dest_code": dest_code,
                        "origin_name": origin_name,
                        "origin_code": origin_code,
                        "migrants": num_migrants,
                        "origin_dem": origin_dem,
                        "dest_dem": dest_dem})
            G.add_node(dest_code, name=dest_name, dem_index=dest_dem)
            G.add_node(origin_code, name=origin_name, dem_index=origin_dem)
            if (num_migrants > MIN_EDGE_WEIGHT):
                G.add_edge(origin_code, dest_code, weight=num_migrants)
    return data

def betweenness_centrality(G):
    betweenness = nx.betweenness_centrality(G)
    sorted_betweenness = sorted(betweenness.items(), key=lambda item: item[1], reverse=True)
    with open("bc_out.txt", "w") as file:
        for node, bc in sorted_betweenness:
            file.write(f"{G.nodes[node]}: {bc}\n")

def clustering_coefficient(G):
    clustering_directed = nx.clustering(G, weight='weight')
    sorted_clustering = sorted(clustering_directed.items(), key=lambda item: item[1], reverse=True)
    with open("cc_out.txt", "w") as file:
        for node, clustering in sorted_clustering:
            file.write(f"{G.nodes[node]}: {clustering}\n")

if __name__ == '__main__':
   main()
