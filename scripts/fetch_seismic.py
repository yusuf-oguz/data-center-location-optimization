import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import sys
sys.path.insert(0, r"D:\_Development\Projects\University_Studies\Opti\Term Project\proje_dosyalari")
from provinces import id_to_tr
sys.stdout.reconfigure(encoding="utf-8")

PARAMETRE  = r"D:\_Development\Projects\University_Studies\Opti\Term Project\proje_dosyalari\data\deprem_afad\parametre.xlsx"
GADM       = r"D:\_Development\Projects\University_Studies\Opti\Term Project\proje_dosyalari\assets\gadm41_TUR.gpkg"
OUTPUT     = r"D:\_Development\Projects\University_Studies\Opti\Term Project\proje_dosyalari\data\deprem_afad\seismic.xlsx"

# --- PGA verisini oku (%10 in 50 year sütunu) ---
df = pd.read_excel(PARAMETRE, header=2, usecols=["Boylam", "Enlem", "% 10"])
df.columns = ["lon", "lat", "pga"]
df = df.dropna()
print(f"Toplam koordinat: {len(df)}")

# --- GADM il sınırlarını yükle ---
turkey = gpd.read_file(GADM, layer="ADM_ADM_1").to_crs("EPSG:4326")

# --- Her koordinatı iline ata ---
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["lon"], df["lat"]), crs="EPSG:4326")
joined = gpd.sjoin(gdf, turkey[["NAME_1", "geometry"]], how="left", predicate="within")

# Sınır dışında kalan noktaları nearest ile eşleştir
unmatched = joined[joined["NAME_1"].isna()].drop(columns=["index_right", "NAME_1"])
if len(unmatched) > 0:
    matched_near = gpd.sjoin_nearest(unmatched, turkey[["NAME_1", "geometry"]], how="left")
    joined = pd.concat([joined[~joined["NAME_1"].isna()], matched_near], ignore_index=True)

print(f"Eşleşmeyen nokta: {joined['NAME_1'].isna().sum()}")

# --- GADM adından province_id'ye çevir ---
from provinces import gadm_to_id
joined["province_id"] = joined["NAME_1"].map(gadm_to_id)
print(f"province_id atanamayan: {joined['province_id'].isna().sum()}")

# --- İl bazlı ortalama PGA ---
result = joined.groupby("province_id")["pga"].mean().reset_index()
result.columns = ["province_id", "pga_mean"]
result["province_id"] = result["province_id"].astype(int)
result = result.sort_values("province_id").reset_index(drop=True)

# --- P skoru: log normalizasyon + ters çevirme (Denklem 6) ---
log_pga = np.log(result["pga_mean"])
result["P"] = 1 - (log_pga - log_pga.min()) / (log_pga.max() - log_pga.min())

result["il_adi_tr"] = result["province_id"].map(id_to_tr)
result = result[["province_id", "il_adi_tr", "pga_mean", "P"]]

print(f"\nSatır sayısı: {len(result)}")
print(result.to_string())

result.to_excel(OUTPUT, index=False)
print(f"\nKaydedildi: {OUTPUT}")
