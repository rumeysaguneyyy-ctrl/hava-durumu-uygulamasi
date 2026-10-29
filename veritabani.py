import sqlite3
import pandas as pd
from datetime import datetime


class Veritabani:
    def __init__(self, db_adi="hava.db"):
        self.db_adi = db_adi
        self.tablo_olustur()

    def tablo_olustur(self):
        baglanti = sqlite3.connect(self.db_adi)
        imlec = baglanti.cursor()
        imlec.execute("""
            CREATE TABLE IF NOT EXISTS sorgular (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sehir TEXT,
                sicaklik REAL,
                ruzgar REAL,
                tarih TEXT
            )
        """)
        baglanti.commit()
        baglanti.close()

    def sorgu_kaydet(self, sehir, sicaklik, ruzgar):
        tarih = datetime.now().strftime("%d.%m.%Y %H:%M")
        baglanti = sqlite3.connect(self.db_adi)
        imlec = baglanti.cursor()
        imlec.execute(
            "INSERT INTO sorgular (sehir, sicaklik, ruzgar, tarih) VALUES (?, ?, ?, ?)",
            (sehir, sicaklik, ruzgar, tarih),
        )
        baglanti.commit()
        baglanti.close()

    def gecmis_tablo(self):
        baglanti = sqlite3.connect(self.db_adi)
        df = pd.read_sql_query(
            "SELECT sehir, sicaklik, ruzgar, tarih FROM sorgular ORDER BY id DESC LIMIT 10",
            baglanti,
        )
        baglanti.close()
        df.columns = ["Şehir", "Sıcaklık (°C)", "Rüzgar (km/s)", "Tarih"]
        return df

    def gecmisi_sil(self):
        baglanti = sqlite3.connect(self.db_adi)
        imlec = baglanti.cursor()
        imlec.execute("DELETE FROM sorgular")
        baglanti.commit()
        baglanti.close()