import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
import streamlit as st
import os
from provinces import *
from dataframe import df
from solver import solver

BASE = os.path.dirname(__file__)

st.title("Multi-Criteria Location Optimization for Data Center Placement in Türkiye")

# geo data
turkey = gpd.read_file(os.path.join(BASE, "assets", "gadm41_TUR.gpkg"), layer="ADM_ADM_1")
turkey = turkey.to_crs("EPSG:4326")
turkey["ID"] = turkey["NAME_1"].map(gadm_to_id)

# solar & wind raw scores for α/β recomputation
solar_df = pd.read_excel(os.path.join(BASE, "data", "enerji_nasa_tureb", "gunes", "solar.xlsx"))[["province_id", "S"]]
wind_df  = pd.read_excel(os.path.join(BASE, "data", "enerji_nasa_tureb", "ruzgar", "wind.xlsx"))[["province_id", "W"]]

# ── Sidebar ──────────────────────────────────────────────────────────────────

st.sidebar.markdown("## Renewable Energy Weights (α / β)")
st.sidebar.caption("E = α × Solar + β × Wind  (auto-normalized so α + β = 1)")
alpha_pct = st.sidebar.slider("Solar weight α (%)", 0, 100, 60, 5)
beta_pct  = 100 - alpha_pct
st.sidebar.write(f"α = {alpha_pct/100:.2f}   β = {beta_pct/100:.2f}")

alpha = alpha_pct / 100.0
beta  = beta_pct  / 100.0

st.sidebar.markdown("---")
st.sidebar.markdown("## Land Slope Threshold (θ)")
st.sidebar.info(
    "θ = 5°  (current dataset)\n\n"
    "F scores are pre-computed for θ = 5°. "
    "To recompute with a different θ, re-run `scripts/fetch_land.py`."
)

st.sidebar.markdown("---")
st.sidebar.markdown("## Suitability Score Weights")
weight_templates = {
    "Equal Weights":               (20, 20, 20, 20, 20),
    "Available Land Priority":     (60, 10, 10, 10, 10),
    "Seismic Priority":            (10, 60, 10, 10, 10),
    "Labor Priority":              (10, 10, 60, 10, 10),
    "Renewable Energy Priority":   (10, 10, 10, 60, 10),
    "Cooling Efficiency Priority": (10, 10, 10, 10, 60),
}

selected_template = st.sidebar.selectbox("Weight Template", list(weight_templates.keys()))
defaults = weight_templates[selected_template]

w_1 = st.sidebar.slider("Land Availability (F)",  0, 100, defaults[0], 1)
w_2 = st.sidebar.slider("Seismic Safety (P)",      0, 100, defaults[1], 1)
w_3 = st.sidebar.slider("Labor Density (L)",       0, 100, defaults[2], 1)
w_4 = st.sidebar.slider("Renewable Energy (E)",    0, 100, defaults[3], 1)
w_5 = st.sidebar.slider("Cooling Efficiency (C)",  0, 100, defaults[4], 1)

weight_total = w_1 + w_2 + w_3 + w_4 + w_5
if weight_total == 0:
    weight_total = 1
w_1n = w_1 / weight_total
w_2n = w_2 / weight_total
w_3n = w_3 / weight_total
w_4n = w_4 / weight_total
w_5n = w_5 / weight_total

st.sidebar.markdown("**Normalized weights:**")
st.sidebar.write(
    f"F={w_1n:.3f}  P={w_2n:.3f}  L={w_3n:.3f}  E={w_4n:.3f}  C={w_5n:.3f}"
)

st.sidebar.markdown("---")
st.sidebar.markdown("## Solver")

budget_mode  = st.sidebar.checkbox("Budget Mode")
budget_limit = None
count_limit  = None
if not budget_mode:
    count_limit  = st.sidebar.number_input("Province Count", min_value=1, value=5, step=1)
else:
    budget_limit = st.sidebar.number_input("Budget Limit (TL)", min_value=0.0, value=1e9, step=1e7, format="%.0f")

min_border  = st.sidebar.number_input("Safety Distance From Border (km)", value=100, step=10)
d_min       = st.sidebar.number_input("Minimum Distance Between Provinces (km)", value=100, step=10)
seismic_min = st.sidebar.number_input("Minimum Seismic Safety Score", value=1.0, step=0.1, format="%.2f")
solve_clicked = st.sidebar.button("Solve!")

# ── Recompute E with current α/β ─────────────────────────────────────────────

provinces = df.copy()
provinces = provinces.merge(solar_df, left_on="province_id", right_on="province_id", how="left")
provinces = provinces.merge(wind_df,  left_on="province_id", right_on="province_id", how="left")
provinces["E"] = alpha * provinces["S"] + beta * provinces["W"]

# ── Merge with GDF ────────────────────────────────────────────────────────────

turkey_gdf = turkey.merge(provinces, left_on="ID", right_on="province_id", how="inner")
turkey_gdf = turkey_gdf.drop(columns=["province_id"])

# ── Suitability score Z ───────────────────────────────────────────────────────

turkey_gdf["Z"] = (
    turkey_gdf["F"] * w_1n +
    turkey_gdf["P"] * w_2n +
    turkey_gdf["L"] * w_3n +
    turkey_gdf["E"] * w_4n +
    turkey_gdf["C"] * w_5n
)

# ── Solver ────────────────────────────────────────────────────────────────────

result_ids       = None
winning_provinces = None

if solve_clicked:
    with st.spinner("Calculating optimal placement..."):
        result_ids = solver(turkey_gdf, budget_mode, budget_limit, count_limit, min_border, seismic_min, d_min)
        if result_ids is not None:
            winning_provinces = turkey_gdf[turkey_gdf["ID"].isin(result_ids)]

# ── Map ───────────────────────────────────────────────────────────────────────

fig, ax = plt.subplots()
fig.set_size_inches(12, 4)
turkey_gdf.plot(column="Z", ax=ax, legend=True, zorder=8)
ax.grid(True, linestyle="--", alpha=0.6, zorder=4)

if winning_provinces is not None:
    winning_provinces.plot(
        column="Z",
        ax=ax,
        cmap="YlOrRd",
        legend=False,
        edgecolor="black",
        linewidth=2,
        zorder=9,
    )

st.pyplot(fig)

# ── Results ───────────────────────────────────────────────────────────────────

if winning_provinces is not None:
    st.success(f"Optimal Solution Found: {len(result_ids)} provinces selected!")
    display_cols = ["ID", "name", "Z", "F", "P", "L", "E", "C", "cost"]
    st.dataframe(
        winning_provinces[display_cols].sort_values("Z", ascending=False).reset_index(drop=True)
    )
elif solve_clicked and result_ids is None:
    st.error("No valid solution found.")
