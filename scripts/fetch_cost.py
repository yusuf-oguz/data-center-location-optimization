import pandas as pd
import numpy as np
import sys
sys.path.insert(0, r"D:\_Development\Projects\University_Studies\Opti\Term Project\proje_dosyalari")
from provinces import id_to_tr, nuts3_to_id
sys.stdout.reconfigure(encoding="utf-8")

GSYH_FILE = r"D:\_Development\Projects\University_Studies\Opti\Term Project\proje_dosyalari\data\gelir_tuik\İl bazında gayrisafi yurt içi hasıla iktisadi faaliyet kollarına (A10) göre cari fiyatlarla 2020-2024.xls"
OUTPUT    = r"D:\_Development\Projects\University_Studies\Opti\Term Project\proje_dosyalari\data\gelir_tuik\cost.xlsx"

# --- Sabitler (Denklem 17: c_i = C_base + P_exp * I_i + E_annual * U_elec) ---
C_BASE   = 50_000_000      # 50M TL — orta ölçekli veri merkezi baz inşaat maliyeti
P_EXP    = 100             # personel sayısı
E_ANNUAL = 10_000_000      # 10 GWh/yıl — yıllık enerji tüketimi (kWh)
# EPDK Nisan 2026: OG Çift Terim Sanayi — tek zamanlı enerji + dağıtım bedeli (kr/kWh → TL/kWh)
U_ELEC   = (290.9687 + 107.0498) / 100  # = 3.9802 TL/kWh

# --- GSYH verisini oku ---
df_raw = pd.read_excel(GSYH_FILE, header=None)

# NUTS-3 kodu sadece ilk yıl satırında dolu, sonraki 4 yıl satırı NaN
# col 0'ı forward-fill yaparak her satıra NUTS-3 kodunu aktar
df_raw[0] = df_raw[0].ffill()

# 2024 yılı satırlarını filtrele
df_2024 = df_raw[df_raw.iloc[:, 2] == 2024].copy()

# NUTS-3 kodu ve GSYH sütunlarını al
df_2024 = df_2024.iloc[:, [0, 16]].copy()
df_2024.columns = ["nuts3", "gsyh"]

# Türkiye toplam ve başlık satırlarını çıkar
df_2024 = df_2024[df_2024["nuts3"].str.match(r"^TR\w{3}$", na=False) & (df_2024["nuts3"] != "TR")].copy()

# province_id eşleştir
df_2024["province_id"] = df_2024["nuts3"].map(nuts3_to_id)
missing = df_2024["province_id"].isna().sum()
print(f"province_id atanamayan: {missing}")
if missing > 0:
    print(df_2024[df_2024["province_id"].isna()][["nuts3"]])

df_2024 = df_2024.dropna(subset=["province_id"])
df_2024["province_id"] = df_2024["province_id"].astype(int)
df_2024 = df_2024.sort_values("province_id").reset_index(drop=True)

# I_i: kişi başı GSYH proxy olarak il GSYH kullan (milyon TL → TL)
df_2024["gsyh_tl"] = df_2024["gsyh"]  # zaten TL cinsinden (bin TL olabilir, kontrol et)

# Maliyet hesapla (Denklem 17)
# I_i olarak il GSYH'yi normalize edip personel maliyeti proxy'si olarak kullanıyoruz
# Önce I_i'yi 0-1 arasına normalize et, sonra C_base ile aynı mertebeye ölçekle
gsyh_min = df_2024["gsyh_tl"].min()
gsyh_max = df_2024["gsyh_tl"].max()
df_2024["I_i"] = (df_2024["gsyh_tl"] - gsyh_min) / (gsyh_max - gsyh_min)

df_2024["cost"] = C_BASE + P_EXP * df_2024["I_i"] * C_BASE + E_ANNUAL * U_ELEC
df_2024["il_adi_tr"] = df_2024["province_id"].map(id_to_tr)

result = df_2024[["province_id", "il_adi_tr", "gsyh_tl", "I_i", "cost"]].copy()

print(f"\nSatır sayısı: {len(result)}")
print(f"Maliyet aralığı: {result['cost'].min()/1e6:.1f}M — {result['cost'].max()/1e6:.1f}M TL")
print(result.to_string())

result.to_excel(OUTPUT, index=False)
print(f"\nKaydedildi: {OUTPUT}")
