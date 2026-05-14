import pandas as pd
import sys
sys.stdout.reconfigure(encoding="utf-8")

SOLAR  = r"D:\_Development\Projects\University_Studies\Opti\Term Project\proje_dosyalari\data\enerji_nasa_tureb\gunes\solar.xlsx"
WIND   = r"D:\_Development\Projects\University_Studies\Opti\Term Project\proje_dosyalari\data\enerji_nasa_tureb\ruzgar\wind.xlsx"
OUTPUT = r"D:\_Development\Projects\University_Studies\Opti\Term Project\proje_dosyalari\data\enerji_nasa_tureb\energy.xlsx"

ALPHA = 0.6  # güneş ağırlığı
BETA  = 0.4  # rüzgar ağırlığı

df_s = pd.read_excel(SOLAR)[["province_id", "il_adi_tr", "ghi", "S"]]
df_w = pd.read_excel(WIND)[["province_id", "wind_mw", "W"]]

df = df_s.merge(df_w, on="province_id", how="inner")

# Denklem 10-12: E = α*S̃ + β*W̃
df["E"] = ALPHA * df["S"] + BETA * df["W"]

print(f"Eksik değer: {df['E'].isna().sum()}")
print(df[["province_id", "il_adi_tr", "ghi", "S", "wind_mw", "W", "E"]].to_string())

df.to_excel(OUTPUT, index=False)
print(f"\nKaydedildi: {OUTPUT}")
