import pandas as pd
import numpy as np
import geopandas as gpd
import pulp
import math
from kgm import impossible_pairs

def solver(df, budget_mode = False, budget_limit = None, count_limit = None, min_border = 100,seismic_min = 1.0, d_min = 100):
    prob = pulp.LpProblem("Province_Selection", pulp.LpMaximize)

    province_ids = df["ID"].tolist()
    scores = dict(zip(df["ID"], df["Z"]))
    costs = dict(zip(df["ID"], df["cost"]))
    seismic_scores = dict(zip(df["ID"], df["P"]))
    conflicting_pairs = impossible_pairs(d_min=d_min)
    lats = dict(zip(df["ID"], df["latitude"]))
    dist_from_border = dict()

    y = pulp.LpVariable.dicts("Province", province_ids, cat=pulp.LpBinary)

    prob += pulp.lpSum([scores[i] * y[i] for i in province_ids]), "Total_Suitability"

    if not budget_mode:
        if count_limit is None:
            raise ValueError("Must provide a count_limit for Count Mode")
        prob += pulp.lpSum([y[i] for i in province_ids]) == count_limit, "Province_Count"

    elif budget_mode:
        if budget_limit is None:
            raise ValueError("Must provide a budget_limit for Budget Mode")
        prob += pulp.lpSum([costs[i] * y[i] for i in province_ids]) <= budget_limit, "Budget_Limit"

    else:
        raise ValueError("Mode must be 'budget' or 'count'")
    
    prob += pulp.lpSum([seismic_scores[i] * y[i] for i in province_ids]) >= seismic_min, "Seismic_Safety"

    for i,j in conflicting_pairs:
        if i in y and j in y:
            prob += y[i] + y[j] <= 1, f"Minimum_Distance_{i}_{j}"

    R = 6371 #in km
    for i,l in lats.items():
        d = R * math.radians(abs(l - 37))
        dist_from_border[i] = d

    for i in province_ids:
        if dist_from_border[i] < min_border:
            prob += y[i] == 0, f"Border_Exclusion_{i}"

    #solve
    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    if pulp.LpStatus[prob.status] != "Optimal":
        return None

    selected_ids = [i for i in province_ids if y[i].varValue  is not None and y[i].varValue > 0.5]
    return selected_ids