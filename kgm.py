import pandas as pd
import numpy as np
import pickle

df = pd.read_excel("assets/ilmesafe.xlsx")
df = df.iloc[1:, 2:]
d_matrix = df.to_numpy(dtype=float)

def impossible_pairs (d_matrix = d_matrix, d_min = 100):
    impossible_pairs = []
    for i in range(1,81):
        for j in range(i):
            if d_matrix[j,i] <= d_min:
                impossible_pairs.append((j + 1,i + 1))
    return impossible_pairs