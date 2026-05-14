import math
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.mask import mask as rio_mask
import sys
sys.path.insert(0, r"D:\_Development\Projects\University_Studies\Opti\Term Project\proje_dosyalari")
from provinces import id_to_tr, gadm_to_id
sys.stdout.reconfigure(encoding="utf-8")

SRTM   = r"D:\_Development\Projects\University_Studies\Opti\Term Project\proje_dosyalari\data\arazi_srtm\turkey_srtm.tif"
GADM   = r"D:\_Development\Projects\University_Studies\Opti\Term Project\proje_dosyalari\assets\gadm41_TUR.gpkg"
OUTPUT = r"D:\_Development\Projects\University_Studies\Opti\Term Project\proje_dosyalari\data\arazi_srtm\land.xlsx"

THETA = 5.0  # eğim eşiği (derece)

turkey = gpd.read_file(GADM, layer="ADM_ADM_1").to_crs("EPSG:4326")
turkey["province_id"] = turkey["NAME_1"].map(gadm_to_id)
turkey = turkey.dropna(subset=["province_id"])
turkey["province_id"] = turkey["province_id"].astype(int)

results = []

with rasterio.open(SRTM) as ds:
    for _, row in turkey.iterrows():
        pid  = row["province_id"]
        name = id_to_tr[pid]
        geom = [row["geometry"].__geo_interface__]
        try:
            elev_masked, transform = rio_mask(ds, geom, crop=True, nodata=-9999)
            elev = elev_masked[0].astype(float)
            valid = elev != -9999

            # Piksel boyutunu metreye çevir
            lat_center = (row["geometry"].bounds[1] + row["geometry"].bounds[3]) / 2
            res_x = abs(transform.a)
            res_y = abs(transform.e)
            m_per_deg_lat = 111320.0
            m_per_deg_lon = 111320.0 * math.cos(math.radians(lat_center))
            dx = res_x * m_per_deg_lon
            dy = res_y * m_per_deg_lat

            elev[~valid] = np.nan
            gy, gx = np.gradient(elev, dy, dx)
            slope_deg = np.degrees(np.arctan(np.sqrt(gx**2 + gy**2)))

            flat = valid & (slope_deg < THETA)
            cell_area_km2 = (dx * dy) / 1e6
            flat_area_km2 = float(flat.sum() * cell_area_km2)

            print(f"{pid:2d} {name}: {flat_area_km2:.1f} km²", flush=True)
        except Exception as e:
            flat_area_km2 = None
            print(f"{pid:2d} {name}: HATA - {e}", flush=True)

        results.append({"province_id": pid, "il_adi_tr": name, "flat_area_km2": flat_area_km2})

df = pd.DataFrame(results).sort_values("province_id").reset_index(drop=True)

f_min = df["flat_area_km2"].min()
f_max = df["flat_area_km2"].max()
df["F"] = (df["flat_area_km2"] - f_min) / (f_max - f_min)

print(f"\nEksik değer: {df['flat_area_km2'].isna().sum()}")
print(df.to_string())

df.to_excel(OUTPUT, index=False)
print(f"\nKaydedildi: {OUTPUT}")
