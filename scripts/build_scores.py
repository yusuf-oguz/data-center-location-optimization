import pandas as pd
import sys
sys.stdout.reconfigure(encoding="utf-8")

BASE = r"D:\_Development\Projects\University_Studies\Opti\Term Project\proje_dosyalari\data"
OUTPUT = r"D:\_Development\Projects\University_Studies\Opti\Term Project\proje_dosyalari\data\processed\scores.csv"
COORDS = r"D:\_Development\Projects\University_Studies\Opti\Term Project\proje_dosyalari\data\koordinatlar\coordinates.csv"

labor   = pd.read_excel(f"{BASE}/isgücü_tuik/labor.xlsx")[["province_id", "L"]]
seismic = pd.read_excel(f"{BASE}/deprem_afad/seismic.xlsx")[["province_id", "P"]]
energy  = pd.read_excel(f"{BASE}/enerji_nasa_tureb/energy.xlsx")[["province_id", "E"]]
land    = pd.read_excel(f"{BASE}/arazi_srtm/land.xlsx")[["province_id", "il_adi_tr", "F"]]
cooling = pd.read_excel(f"{BASE}/sicaklik_mgm/cooling.xlsx")[["province_id", "C"]]
cost    = pd.read_excel(f"{BASE}/gelir_tuik/cost.xlsx")[["province_id", "cost"]]
coords  = pd.read_csv(COORDS)[["province_id", "latitude", "longitude"]]

df = land.copy()
for other in [labor, seismic, energy, cooling, cost, coords]:
    df = df.merge(other, on="province_id", how="inner")

df = df.rename(columns={"il_adi_tr": "name"})
df = df.rename(columns={"province_id": "ID"})
df = df[["ID", "name", "latitude", "longitude", "F", "P", "L", "E", "C", "cost"]]
df = df.sort_values("ID").reset_index(drop=True)

print(f"Satir: {len(df)}")
print(f"Sutunlar: {list(df.columns)}")
print(f"NaN: {df.isna().sum().sum()}")
print(df.to_string())

import os
os.makedirs(r"D:\_Development\Projects\University_Studies\Opti\Term Project\proje_dosyalari\data\processed", exist_ok=True)
df.to_csv(OUTPUT, index=False, encoding="utf-8-sig")
print(f"\nKaydedildi: {OUTPUT}")
