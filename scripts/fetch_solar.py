import pandas as pd
import numpy as np
import requests
import time
import sys
sys.path.insert(0, r"D:\_Development\Projects\University_Studies\Opti\Term Project\proje_dosyalari")
from provinces import id_to_tr
sys.stdout.reconfigure(encoding="utf-8")

COORDINATES = r"D:\_Development\Projects\University_Studies\Opti\Term Project\proje_dosyalari\data\koordinatlar\coordinates.csv"
OUTPUT      = r"D:\_Development\Projects\University_Studies\Opti\Term Project\proje_dosyalari\data\enerji_nasa_tureb\gunes\solar.xlsx"

NASA_URL = "https://power.larc.nasa.gov/api/temporal/climatology/point"

def fetch_ghi(lat, lon):
    params = {
        "parameters": "ALLSKY_SFC_SW_DWN",
        "community": "SB",
        "latitude": lat,
        "longitude": lon,
        "format": "JSON",
    }
    r = requests.get(NASA_URL, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    # ANN: yıllık ortalama
    ann = data["properties"]["parameter"]["ALLSKY_SFC_SW_DWN"]["ANN"]
    return float(ann)

df_coords = pd.read_csv(COORDINATES)
results = []

for _, row in df_coords.iterrows():
    pid  = int(row["province_id"])
    lat  = row["latitude"]
    lon  = row["longitude"]
    name = id_to_tr[pid]
    try:
        ghi = fetch_ghi(lat, lon)
        print(f"{pid:2d} {name}: {ghi:.4f} kWh/m²/gün")
    except Exception as e:
        ghi = None
        print(f"{pid:2d} {name}: HATA - {e}")
    results.append({"province_id": pid, "il_adi_tr": name, "ghi": ghi})
    time.sleep(0.5)

df = pd.DataFrame(results)

# Normalizasyon
df["S"] = (df["ghi"] - df["ghi"].min()) / (df["ghi"].max() - df["ghi"].min())

print(f"\nEksik değer: {df['ghi'].isna().sum()}")
print(df.to_string())

df.to_excel(OUTPUT, index=False)
print(f"\nKaydedildi: {OUTPUT}")
