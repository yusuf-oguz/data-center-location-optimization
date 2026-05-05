import osmnx as ox
import pandas as pd
from provinces import *
import time
import csv

def get_latitude(id):
    city_name = id_to_en[id]
    query = f"{city_name}, Turkey"
    try:
        lat, lon = ox.geocode(query)
        print(id,lat)
        return lat
    except Exception as e:
        print(f"Could not find {query}: {e}")
        return None

def pull_latitudes(file_path = "data/latitudes.csv"):
    try:
        df_lats = pd.read_csv(file_path)
        print("Read the CSV")

    except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError):
        print("Could not read the CSV")
        latitudes = [] 
        for i in range(1, 82): 
            latitudes.append([i, get_latitude(i)]) 
    
        with open(file_path, mode='w', newline='') as file: 
            writer = csv.writer(file) 
            writer.writerow(["province_id", "latitude"]) 
            writer.writerows(latitudes)
        
        df_lats = pd.DataFrame(latitudes, columns=["province_id", "latitude"])
    return df_lats