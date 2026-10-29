import requests


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

    def sehir_hava(self, sehir):
        konum = self.konum_bul(sehir)

        if konum is None:
            return None

        enlem, boylam = konum
        return self.hava_getir(enlem, boylam)