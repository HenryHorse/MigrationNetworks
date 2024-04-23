

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



pos = nx.spring_layout(G)  # positions for all nodes

# nodes
nx.draw_networkx_nodes(G, pos, node_size=700)

# edges
edges = nx.draw_networkx_edges(G, pos, width=6)

# labels
nx.draw_networkx_labels(G, pos, font_size=20, font_family='sans-serif')

plt.axis('off')  # Turn off the axis
plt.show()

