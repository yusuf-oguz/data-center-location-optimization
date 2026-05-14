import osmnx as ox
import pandas as pd
from provinces import *
import csv

def get_coordinates(id):
    city_name = id_to_en[id]
    query = f"{city_name}, Turkey"
    try:
        lat, lon = ox.geocode(query)
        print(f"{id} {id_to_tr[id]}: {lat}, {lon}")
        return lat, lon
    except Exception as e:
        print(f"Could not find {query}: {e}")
        return None, None

def pull_coordinates(file_path="data/koordinatlar/coordinates.csv"):
    try:
        df = pd.read_csv(file_path)
        print("Read the CSV")
    except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError):
        print("Could not read the CSV, fetching from OSM...")
        coords = []
        for i in range(1, 82):
            lat, lon = get_coordinates(i)
            coords.append([i, lat, lon])

        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["province_id", "latitude", "longitude"])
            writer.writerows(coords)

        df = pd.DataFrame(coords, columns=["province_id", "latitude", "longitude"])
    return df
