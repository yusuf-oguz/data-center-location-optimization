# Multi-Criteria Location Optimization for Data Center Placement in Türkiye

**YZV 202E - Optimization for Data Science, Spring 2026**  
Istanbul Technical University — Osmancan Sarı, Efe Karan Hacımustafaoğlu, Yusuf Oğuz

---

## Problem

Selecting optimal provinces in Türkiye for data center placement by balancing five competing criteria using Binary Integer Programming (BIP).

| Criterion | Symbol | Source |
|-----------|--------|--------|
| Land Availability (slope < 5°) | F | SRTM 90m (OpenTopography) |
| Seismic Safety (inverted PGA) | P | AFAD |
| Labor Density | L | TÜİK |
| Renewable Energy (solar + wind) | E | NASA POWER + TÜREB |
| Cooling Efficiency (inverted temperature) | C | MGM |

Cost model derived from TÜİK GDP (2024) and EPDK electricity tariffs.

---

## Model

**Suitability score:**  
`x_i = w1*F_i + w2*P_i + w3*L_i + w4*E_i + w5*C_i`

**Objective:**  
`max Z = sum(x_i * y_i),  y_i in {0, 1}`

**Constraints:**
- C1: Count mode (`sum(y_i) = K`) or Budget mode (`sum(c_i * y_i) <= B`)
- C2: Minimum distance between selected provinces
- C3: Seismic safety floor
- C4: Border exclusion zone
- C5: Binary domain

Solved with **PuLP + CBC** (Branch and Cut).

---

## Repository Structure

```
proje_dosyalari/
├── app.py                  # Streamlit interactive dashboard
├── solver.py               # BIP solver (PuLP + CBC)
├── dataframe.py            # Data loader
├── distance.py             # Distance constraint helper
├── provinces.py            # Province ID mappings
├── notebook.ipynb          # Full analysis notebook
├── notebook.pdf            # Exported notebook (PDF)
├── figures/                # Generated plots
│   ├── criterion_scores.png
│   ├── correlation_matrix.png
│   ├── suitability_map.png
│   ├── result_map.png
│   └── cbc_vs_greedy.png
├── data/
│   ├── processed/scores.csv        # Merged scores (81 provinces)
│   ├── arazi_srtm/land.xlsx        # F scores
│   ├── deprem_afad/seismic.xlsx    # P scores
│   ├── isgücü_tuik/labor.xlsx      # L scores
│   ├── enerji_nasa_tureb/energy.xlsx # E scores
│   ├── sicaklik_mgm/cooling.xlsx   # C scores
│   └── gelir_tuik/cost.xlsx        # Cost estimates
├── scripts/
│   ├── fetch_land.py
│   ├── fetch_seismic.py
│   ├── fetch_labor.py
│   ├── fetch_solar.py
│   ├── fetch_wind.py
│   ├── fetch_energy.py
│   ├── fetch_cooling.py
│   ├── fetch_cost.py
│   └── build_scores.py
└── assets/
    └── gadm41_TUR.gpkg     # GADM Turkey province boundaries
```

---

## Running the Project

**Requirements:** Python 3.12, dependencies in `.venv`

```bash
# Install dependencies
uv venv
uv pip install -r requirements.txt

# Run interactive dashboard
streamlit run app.py

# Open notebook
jupyter lab notebook.ipynb
```

---

## Data Sources

- **SRTM:** OpenTopography API (90m resolution)
- **AFAD:** Peak Ground Acceleration, 10% probability in 50 years
- **TÜİK:** Provincial employment and GDP 2024
- **NASA POWER:** Annual mean GHI per province centroid
- **TÜREB:** Installed wind capacity by province (July 2022 report)
- **MGM:** Annual mean temperature by province (web scraping)
- **KGM:** Inter-provincial road distance matrix
- **GADM:** Administrative boundaries (gadm.org)
