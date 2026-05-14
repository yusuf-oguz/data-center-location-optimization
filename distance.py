import pandas as pd
import numpy as np

df = pd.read_excel("data/mesafe_kgm/ilmesafe.xlsx")
df = df.iloc[1:, 2:]
d_matrix = df.to_numpy(dtype=float)

def impossible_pairs(d_matrix=d_matrix, d_min=100):
    pairs = []
    for i in range(1, 82):       # province_id 1..81
        for j in range(1, i):    # province_id 1..i-1
            if d_matrix[j - 1, i - 1] <= d_min:
                pairs.append((j, i))
    return pairs