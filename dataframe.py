import pandas as pd
import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

SCORES_CSV = os.path.join(os.path.dirname(__file__), "data", "processed", "scores.csv")

df = pd.read_csv(SCORES_CSV)
df = df.rename(columns={"ID": "province_id"})
df = df[["province_id", "name", "latitude", "longitude", "F", "P", "L", "E", "C", "cost"]]

print(df)