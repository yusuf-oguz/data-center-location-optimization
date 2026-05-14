import pandas as pd
import numpy as np
import sys
sys.path.insert(0, r"D:\_Development\Projects\University_Studies\Opti\Term Project\proje_dosyalari")
from provinces import id_to_tr
sys.stdout.reconfigure(encoding="utf-8")

OUTPUT = r"D:\_Development\Projects\University_Studies\Opti\Term Project\proje_dosyalari\data\enerji_nasa_tureb\ruzgar\wind.xlsx"

# TÜREB Temmuz 2022 raporu, Bölüm 2.4 — il bazlı işletmedeki kurulu rüzgar kapasitesi (MW)
# Kaynakta görünmeyen iller: 0 MW
WIND_MW = {
    35: 1907.10,  # İzmir
    10: 1401.65,  # Balıkesir
    17:  938.05,  # Çanakkale
    34:  859.59,  # İstanbul
    45:  727.55,  # Manisa
    39:  481.68,  # Kırklareli
    31:  437.85,  # Hatay
     3:  368.45,  # Afyonkarahisar
     9:  365.60,  # Aydın
    16:  343.40,  # Bursa
    42:  337.80,  # Konya
    77:  296.75,  # Yalova
    54:  277.00,  # Sakarya
    38:  274.35,  # Kayseri
    80:  265.30,  # Osmaniye
    33:  253.55,  # Mersin
    48:  237.25,  # Muğla
    59:  187.95,  # Tekirdağ
    40:  168.00,  # Kırşehir
    11:  164.50,  # Bilecik
    58:  155.30,  # Sivas
     5:  141.10,  # Amasya
    60:  140.70,  # Tokat
    46:  121.50,  # Kahramanmaraş
    22:   98.40,  # Edirne
    20:   74.80,  # Denizli
    41:   70.80,  # Kocaeli
    27:   65.55,  # Gaziantep
    32:   61.20,  # Isparta
    55:   56.00,  # Samsun
    64:   54.00,  # Uşak
    65:   53.20,  # Van
    26:   52.80,  # Eskişehir
    71:   43.20,  # Kırıkkale
    69:   40.00,  # Bayburt
     2:   27.50,  # Adıyaman
     4:   23.40,  # Ağrı
     1:   16.60,  # Adana
    57:   12.60,  # Sinop
    52:   12.00,  # Ordu
    44:   11.70,  # Malatya
    13:    4.80,  # Bitlis
    18:    4.20,  # Çankırı
    70:    3.60,  # Karaman
    12:    3.50,  # Bingöl
}

records = []
for pid in range(1, 82):
    mw = WIND_MW.get(pid, 0.0)
    records.append({"province_id": pid, "il_adi_tr": id_to_tr[pid], "wind_mw": mw})

df = pd.DataFrame(records)

w_min = df["wind_mw"].min()
w_max = df["wind_mw"].max()
df["W"] = (df["wind_mw"] - w_min) / (w_max - w_min)

print(f"Toplam kurulu kapasite: {df['wind_mw'].sum():.2f} MW")
print(f"Sıfır kapasiteli il sayısı: {(df['wind_mw'] == 0).sum()}")
print(df.to_string())

df.to_excel(OUTPUT, index=False)
print(f"\nKaydedildi: {OUTPUT}")
