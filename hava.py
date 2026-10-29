import requests
from datetime import datetime


class HavaServisi:
    def __init__(self):
        self.konum_url = "https://geocoding-api.open-meteo.com/v1/search"
        self.hava_url = "https://api.open-meteo.com/v1/forecast"

    def konum_bul(self, sehir):
        cevap = requests.get(
            self.konum_url, params={"name": sehir, "count": 1, "language": "tr"}
        )
        veri = cevap.json()

        if "results" not in veri:
            return None

        sonuc = veri["results"][0]
        return sonuc["latitude"], sonuc["longitude"]

    def hava_getir(self, enlem, boylam):
        parametreler = {
            "latitude": enlem,
            "longitude": boylam,
            "current": "temperature_2m,wind_speed_10m",
            "timezone": "auto",
        }
        veri = requests.get(self.hava_url, params=parametreler).json()

        sicaklik = veri["current"]["temperature_2m"]
        ruzgar = veri["current"]["wind_speed_10m"]
        return sicaklik, ruzgar

    def tahmin_getir(self, enlem, boylam):
        parametreler = {
            "latitude": enlem,
            "longitude": boylam,
            "daily": "temperature_2m_max,temperature_2m_min",
            "forecast_days": 5,
            "timezone": "auto",
        }
        veri = requests.get(self.hava_url, params=parametreler).json()

        tarihler = veri["daily"]["time"]
        en_yuksek = veri["daily"]["temperature_2m_max"]
        en_dusuk = veri["daily"]["temperature_2m_min"]

        tahmin = []
        for i in range(len(tarihler)):
            gun = datetime.strptime(tarihler[i], "%Y-%m-%d").strftime("%d.%m")
            tahmin.append((gun, en_yuksek[i], en_dusuk[i]))

        return tahmin

    def sehir_hava(self, sehir):
        konum = self.konum_bul(sehir)

        if konum is None:
            return None

        enlem, boylam = konum
        return self.hava_getir(enlem, boylam)

    def uyari_mesaji(self, sicaklik):
        if sicaklik < 0:
            return "❄️ Hava dondurucu! Çok kalın giyin, buzlanmaya dikkat et."
        elif sicaklik < 10:
            return "🧥 Hava çok soğuk, kalın giyin."
        elif sicaklik < 20:
            return "🧣 Hava serin, yanına bir hırka al."
        elif sicaklik < 30:
            return "😊 Hava çok güzel, keyfini çıkar!"
        else:
            return "☀️ Hava çok sıcak, bol su iç ve güneşten korun."
