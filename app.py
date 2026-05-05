import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
import streamlit as st
from provinces import *
from dataframe import df
from solver import solver

st.title("Multi-Criteria Location Optimization for Data Center Placement in Türkiye")



turkey = gpd.read_file("assets/gadm41_TUR.gpkg", layer="ADM_ADM_1") 
turkey = turkey.to_crs("EPSG:4326")
turkey["ID"] = turkey["NAME_1"].map(gadm_to_id)
provinces = df
turkey_gdf = turkey.merge(provinces, left_on="ID", right_on="province_id", how="inner")
turkey_gdf = turkey_gdf.drop(columns=["province_id"])
print(turkey_gdf.head())



#suitability score
w_1 = st.sidebar.slider("Land Availability Weight",0,100,20,1)
w_2 = st.sidebar.slider("Seismic Safety Weight",0,100,20,1)
w_3 = st.sidebar.slider("Labor Density Weight",0,100,20,1)
w_4 = st.sidebar.slider("Renewable Energy Weight",0,100,20,1)
w_5 = st.sidebar.slider("Cooling Efficiency Weight",0,100,20,1)

weight_total = 1 if w_1 + w_2 + w_3 + w_4 + w_5 == 0 else w_1 + w_2 + w_3 + w_4 + w_5

w_1 = 100 * w_1/weight_total
w_2 = 100 * w_2/weight_total
w_3 = 100 * w_3/weight_total
w_4 = 100 * w_4/weight_total
w_5 = 100 * w_5/weight_total

st.sidebar.markdown("### Relative Weights ###")
st.sidebar.write(f"{w_1:.1f}, {w_2:.1f}, {w_3:.1f}, {w_4:.1f}, {w_5:.1f}")

turkey_gdf["Z"] = (turkey_gdf["F"] * w_1 + turkey_gdf["P"] * w_2 + turkey_gdf["L"] * w_3 + turkey_gdf["E"] * w_4 + turkey_gdf["C"] * w_5)

#draw the map
fig, ax = plt.subplots()
turkey_gdf.plot(column="Z", ax=ax, legend = True)
st.pyplot(fig)

#solver
st.sidebar.markdown("### Solver ###")

budget_mode = st.sidebar.checkbox("Budget Mode")
budget_limit = None
count_limit = None
if not budget_mode:
    count_limit = st.sidebar.number_input("Province Count", min_value=1, value=5, step=1)
elif budget_mode:
    budget_limit = st.sidebar.number_input("Budget Limit", min_value=0.0, value=1e9, step=1e7)
min_border = st.sidebar.number_input("Safety Distance From The Border", value = 100)
d_min = st.sidebar.number_input("Minimum Distance Between Provinces", value = 100)
seismic_min = st.sidebar.number_input("Minimum Seismic Safety Score", value = 0.5)
solve_clicked = st.sidebar.button("Solve!")
if solve_clicked:
    with st.spinner("Calculating optimal placement..."):
        result_ids = solver(turkey_gdf, budget_mode, budget_limit, count_limit, min_border, seismic_min, d_min)
        
        if result_ids is None:
            st.error("No valid solution found.")
        else:
            st.success(f"Optimal Solution Found: {len(result_ids)} provinces selected!")
            
            # Filter your GeoDataFrame to just the winning provinces
            winning_provinces = turkey_gdf[turkey_gdf["ID"].isin(result_ids)]
            st.dataframe(winning_provinces[["name", "Z", "cost"]])