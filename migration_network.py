

'''
1) open the file for reading
2) put all lines into an array using readlines()
3) separate all lines by comma
4) have a list of region codes you don't want to include
5) go through the array, if either destination or origin is in the list of 
regions you don't want to include, exclude the element
6
'''

f = open("undesa_pd_2020_ims_stock_by_sex_destination_and_origin.csv", "r")
csv_lines = f.readlines()
csv_lines = csv_lines[11:]
split_lines = []
for line in csv_lines:
    split_lines.append(line.split(','))
print(split_lines[0][1])
print(split_lines[0][3])
print(split_lines[0][5])
print(split_lines[0][6])
for i in range(7, 14):
    print(split_lines[0][i])


non_countries = ['900', '947', '1833', '921', '1832', '1830', '1835', '927', '1829', '901', '902', '934', \
                 '948', '941', '1636', '1637', '1503', '1517', '1502', '1501', '1500', '903', '910', '911', \
                    '912', '913', '914', '935', '5500', '906', '920', '5501', '922', '908', '923', '924', \
                        '925', '926', '904', '915', '916', '931', '905', '909', '927', '928', '954', '957']
countries_list = []
print(len(split_lines))
for line in split_lines:
    if (line[3] not in non_countries and line[6] not in non_countries
        and line[3].isnumeric() and line[6].isnumeric()):
        countries_list.append(line)
print(len(countries_list))
# Index 1 is destination name, index 3 is destination code
# Index 5 is origin name, index 6 is origin code
# Indices 7-13 are the years from 1990-2020 in increments of 5 years
# List of all non country codes

