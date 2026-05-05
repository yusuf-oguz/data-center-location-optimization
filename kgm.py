import pandas as pd
import numpy as np
import pickle
import csv

df = pd.DataFrame()
try:
    df = pd.read_csv("data/ilmesave.csv")
except:
    df = pd.read_excel("data/ilmesafe.xlsx")
    df = df.iloc[1:, 2:]
    df.to_csv("data/ilmesafe.csv")
d_matrix = df.to_numpy(dtype=float)
print(d_matrix)

def impossible_pairs (d_matrix = d_matrix, d_min = 100):
    impossible_pairs = []
    for i in range(1,81):
        for j in range(i):
            if d_matrix[j,i] <= d_min:
                impossible_pairs.append((j + 1,i + 1))
    return impossible_pairs