import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
from provinces import *
from pull_latitude import pull_latitudes as pl

df = pd.DataFrame({
    "province_id": range(1, 82),
    "name": [id_to_tr[i] for i in range(1, 82)],
    "F": np.random.rand(81),  # land availability
    "P": np.random.rand(81),  # seismic safety
    "L": np.random.rand(81),  # labor density
    "E": np.random.rand(81),  # renewable energy
    "C": np.random.rand(81),  # cooling efficiency
    "cost": np.random.uniform(1e8, 5e8, 81)
})

df_lats = pl()

df = df.merge(df_lats,left_on="province_id",right_on="province_id",how="inner")

print(df)