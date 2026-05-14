import requests
import numpy as np
import pandas as pd
import time
from bs4 import BeautifulSoup
import sys
sys.path.insert(0, r"D:\_Development\Projects\University_Studies\Opti\Term Project\proje_dosyalari")
from provinces import id_to_en, id_to_tr
sys.stdout.reconfigure(encoding="utf-8")

OUTPUT = r"D:\_Development\Projects\University_Studies\Opti\Term Project\proje_dosyalari\data\sicaklik_mgm\cooling.xlsx"

HEADERS = {"User-Agent": "Mozilla/5.0"}
MGM_URL = "https://www.mgm.gov.tr/veridegerlendirme/il-ve-ilceler-istatistik.aspx"

# MGM sitesindeki ASCII il adları (nav_iller'den alındı), province_id sırasıyla
MGM_NAMES = [
    "ADANA", "ADIYAMAN", "AFYONKARAHISAR", "AGRI", "AMASYA", "ANKARA", "ANTALYA",
    "ARTVIN", "AYDIN", "BALIKESIR", "BILECIK", "BINGOL", "BITLIS", "BOLU", "BURDUR",
    "BURSA", "CANAKKALE", "CANKIRI", "CORUM", "DENIZLI", "DIYARBAKIR", "EDIRNE",
    "ELAZIG", "ERZINCAN", "ERZURUM", "ESKISEHIR", "GAZIANTEP", "GIRESUN", "GUMUSHANE",
    "HAKKARI", "HATAY", "ISPARTA", "ICEL", "ISTANBUL", "IZMIR", "KARS", "KASTAMONU",
    "KAYSERI", "KIRKLARELI", "KIRSEHIR", "KOCAELI", "KONYA", "KUTAHYA", "MALATYA",
    "MANISA", "KAHRAMANMARAS", "MARDIN", "MUGLA", "MUS", "NEVSEHIR", "NIGDE", "ORDU",
    "RIZE", "SAKARYA", "SAMSUN", "SIIRT", "SINOP", "SIVAS", "TEKIRDAG", "TOKAT",
    "TRABZON", "TUNCELI", "SANLIURFA", "USAK", "VAN", "YOZGAT", "ZONGULDAK", "AKSARAY",
    "BAYBURT", "KARAMAN", "KIRIKKALE", "BATMAN", "SIRNAK", "BARTIN", "ARDAHAN",
    "IGDIR", "YALOVA", "KARABUK", "KILIS", "OSMANIYE", "DUZCE",
]  # province_id 1..81 sırasıyla

def fetch_temp(pid):
    name = MGM_NAMES[pid - 1]
    for k in ["H", "A"]:
        url = f"{MGM_URL}?k={k}&m={name}"
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, "html.parser")
        vals = []
        for i in range(1, 13):
            td = soup.find("td", id=f"d{i:02d}")
            if td and td.text.strip():
                try:
                    vals.append(float(td.text.strip().replace(",", ".")))
                except ValueError:
                    pass
        if len(vals) == 12:
            return round(float(np.mean(vals)), 2)
    raise ValueError(f"Eksik ay verisi: {len(vals)}/12")

results = []
for pid in range(1, 82):
    name = id_to_tr[pid]
    try:
        temp = fetch_temp(pid)
        print(f"{pid:2d} {name}: {temp}°C", flush=True)
    except Exception as e:
        temp = None
        print(f"{pid:2d} {name}: HATA - {e}", flush=True)
    results.append({"province_id": pid, "il_adi_tr": name, "temp_avg": temp})
    time.sleep(0.3)

df = pd.DataFrame(results)

# C skoru: ters min-max (düşük sıcaklık = yüksek soğutma verimliliği, Denklem 13)
t_min = df["temp_avg"].min()
t_max = df["temp_avg"].max()
df["C"] = 1 - (df["temp_avg"] - t_min) / (t_max - t_min)

print(f"\nEksik değer: {df['temp_avg'].isna().sum()}")
print(df.to_string())

df.to_excel(OUTPUT, index=False)
print(f"\nKaydedildi: {OUTPUT}")
