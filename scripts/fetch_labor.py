import pandas as pd
import numpy as np
import sys
sys.path.insert(0, r"D:\_Development\Projects\University_Studies\Opti\Term Project\proje_dosyalari")
from provinces import nuts3_to_id, id_to_tr
sys.stdout.reconfigure(encoding="utf-8")

ISGUCUGOSTERGELERI = r"D:\_Development\Projects\University_Studies\Opti\Term Project\proje_dosyalari\data\isgücü_tuik\İl düzeyinde işgücü göstergeleri.csv"
NUFUS             = r"D:\_Development\Projects\University_Studies\Opti\Term Project\proje_dosyalari\data\isgücü_tuik\İl, medeni durum ve cinsiyete göre nüfus.csv"
OUTPUT            = r"D:\_Development\Projects\University_Studies\Opti\Term Project\proje_dosyalari\data\isgücü_tuik\labor.xlsx"

# --- İstihdam oranı ---
df_isgucu = pd.read_csv(ISGUCUGOSTERGELERI, encoding="iso-8859-9", header=None, skiprows=7, nrows=81)
df_isgucu = df_isgucu.iloc[:, [0, 1, 7]].copy()
df_isgucu.columns = ["nuts3", "il_adi", "istihdam_orani"]
df_isgucu = df_isgucu.reset_index(drop=True)

# --- 15+ nüfus (2023) ---
df_nufus = pd.read_csv(NUFUS, encoding="iso-8859-9", header=None, skiprows=8, nrows=82)
df_nufus = df_nufus.iloc[:, [1, 2]].copy()
df_nufus.columns = ["il_adi", "nufus_15plus"]
df_nufus = df_nufus[~df_nufus["il_adi"].astype(str).str.contains("Toplam", na=True)].reset_index(drop=True)
df_nufus["nufus_15plus"] = df_nufus["nufus_15plus"].astype(str).str.replace(" ", "").str.strip().astype(int)

# --- province_id ekle ---
df_isgucu["province_id"] = df_isgucu["nuts3"].map(nuts3_to_id)

# --- Birleştir ---
df = pd.merge(df_isgucu, df_nufus, on="il_adi", how="inner")
df["l_raw"] = df["nufus_15plus"] * df["istihdam_orani"] / 100
df["il_adi_tr"] = df["province_id"].map(id_to_tr)

# --- L skoru: log + min-max normalizasyon (Denklem 7-9) ---
df["l_adj"] = np.log(df["l_raw"])
df["L"] = (df["l_adj"] - df["l_adj"].min()) / (df["l_adj"].max() - df["l_adj"].min())

df = df[["province_id", "il_adi_tr", "istihdam_orani", "nufus_15plus", "l_raw", "l_adj", "L"]].sort_values("province_id").reset_index(drop=True)

print(f"Satır sayısı: {len(df)}")
print(df.to_string())

df.to_excel(OUTPUT, index=False)
print(f"\nKaydedildi: {OUTPUT}")
