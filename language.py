import pandas as pd

# Load each dataset
countries = pd.read_csv('country_list.txt')
languages = pd.read_csv('language_list.txt')
colonies = pd.read_csv('colonies_data.txt')

# Example of using Pandas to align data for visualization without permanently merging
merged_data = pd.merge(colonies, countries, how='left', left_on='Colony', right_on='Country')
merged_data = pd.merge(merged_data, languages, how='left', on='Country')


merged_data