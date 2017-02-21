# deal with cityracks
import pandas as pd
cityracks = pd.read_csv('cityracks.csv',names =["id", "key1","value","type1"])
cityracks['key'] = cityracks['key1'].apply(lambda x: x.split(".")[-1])
cityracks['type'] = 'cityracks'
city_racks = cityracks.drop(['key1','type1'], axis=1)
city_racks.head()