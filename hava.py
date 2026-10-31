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
            "current": "temperature_2m,wind_speed_10m,weather_code",
            "timezone": "auto",
        }
        veri = requests.get(self.hava_url, params=parametreler).json()

        sicaklik = veri["current"]["temperature_2m"]
        ruzgar = veri["current"]["wind_speed_10m"]
        kod = veri["current"]["weather_code"]
        return sicaklik, ruzgar, kod

    def tahmin_getir(self, enlem, boylam):
        parametreler = {
            "latitude": enlem,
            "longitude": boylam,
            "daily": "weather_code,temperature_2m_max,temperature_2m_min",
            "forecast_days": 5,
            "timezone": "auto",
        }
        veri = requests.get(self.hava_url, params=parametreler).json()

        tarihler = veri["daily"]["time"]
        kodlar = veri["daily"]["weather_code"]
        en_yuksek = veri["daily"]["temperature_2m_max"]
        en_dusuk = veri["daily"]["temperature_2m_min"]

        tahmin = []
        for i in range(len(tarihler)):
            gun = datetime.strptime(tarihler[i], "%Y-%m-%d").strftime("%d.%m")
            emoji, yazi = self.durum_bul(kodlar[i])
            tahmin.append((gun, f"{emoji} {yazi}", en_yuksek[i], en_dusuk[i]))

        return tahmin

    def sehir_hava(self, sehir):
        konum = self.konum_bul(sehir)

        if konum is None:
            return None

        enlem, boylam = konum
        return self.hava_getir(enlem, boylam)

    def durum_bul(self, kod):
        durumlar = {
            0: ("☀️", "Güneşli"),
            1: ("🌤️", "Çoğunlukla açık"),
            2: ("⛅", "Parçalı bulutlu"),
            3: ("☁️", "Bulutlu"),
            45: ("🌫️", "Sisli"),
            48: ("🌫️", "Sisli"),
            51: ("🌦️", "Hafif çiseleme"),
            53: ("🌦️", "Çiseleme"),
            55: ("🌦️", "Yoğun çiseleme"),
            56: ("🌧️", "Dondurucu çiseleme"),
            57: ("🌧️", "Dondurucu çiseleme"),
            61: ("🌧️", "Hafif yağmurlu"),
            63: ("🌧️", "Yağmurlu"),
            65: ("🌧️", "Şiddetli yağmurlu"),
            66: ("🌧️", "Dondurucu yağmur"),
            67: ("🌧️", "Dondurucu yağmur"),
            71: ("❄️", "Hafif kar yağışlı"),
            73: ("❄️", "Kar yağışlı"),
            75: ("❄️", "Yoğun kar yağışlı"),
            77: ("❄️", "Kar taneleri"),
            80: ("🌦️", "Hafif sağanak"),
            81: ("🌧️", "Sağanak yağış"),
            82: ("🌧️", "Şiddetli sağanak"),
            85: ("❄️", "Kar sağanağı"),
            86: ("❄️", "Yoğun kar sağanağı"),
            95: ("⛈️", "Gök gürültülü fırtına"),
            96: ("⛈️", "Dolulu fırtına"),
            99: ("⛈️", "Şiddetli dolulu fırtına"),
        }
        return durumlar.get(kod, ("🌡️", "Bilinmiyor"))

    def yagisli_mi(self, kod):
        return kod in [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82, 95, 96, 99]

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
