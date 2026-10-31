import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from hava import HavaServisi
from veritabani import Veritabani

hava_servisi = HavaServisi()
db = Veritabani()


def hava_goster(sehir):
    konum = hava_servisi.konum_bul(sehir)

    if konum is None:
        st.error("Şehir bulunamadı, tekrar dene.")
        return

    enlem, boylam = konum
    sicaklik, ruzgar, kod = hava_servisi.hava_getir(enlem, boylam)
    emoji, durum = hava_servisi.durum_bul(kod)
    db.sorgu_kaydet(sehir, sicaklik, ruzgar)

    st.subheader(sehir)
    st.markdown(f"## {emoji} {durum}")

    sol, sag = st.columns(2)
    sol.metric("Sıcaklık", f"{sicaklik} °C")
    sag.metric("Rüzgar", f"{ruzgar} km/s")

    st.info(hava_servisi.uyari_mesaji(sicaklik))

    if hava_servisi.yagisli_mi(kod):
        st.warning("☂️ Yağış var, şemsiyeni almayı unutma!")

    st.subheader("5 Günlük Tahmin")
    tahmin = hava_servisi.tahmin_getir(enlem, boylam)
    tahmin_df = pd.DataFrame(
        tahmin, columns=["Gün", "Durum", "En Yüksek (°C)", "En Düşük (°C)"]
    )
    st.dataframe(tahmin_df, use_container_width=True, hide_index=True)

    fig, ax = plt.subplots()
    ax.plot(tahmin_df["Gün"], tahmin_df["En Yüksek (°C)"], marker="o", label="En yüksek")
    ax.plot(tahmin_df["Gün"], tahmin_df["En Düşük (°C)"], marker="o", label="En düşük")
    ax.set_ylabel("Sıcaklık (°C)")
    ax.set_title(f"{sehir} - 5 günlük tahmin")
    ax.legend()
    st.pyplot(fig)


st.title("Hava Durumu Uygulaması")

sehir = st.text_input("Şehir adı", "Istanbul").strip()

sol, sag = st.columns(2)
getir = sol.button("Hava Durumunu Getir")
favori_ekle = sag.button("⭐ Favorilere Ekle")

goster = None

if getir:
    goster = sehir

if favori_ekle:
    if hava_servisi.konum_bul(sehir) is None:
        st.error("Şehir bulunamadı, favoriye eklenemedi.")
    else:
        db.favori_ekle(sehir)
        st.success(f"{sehir} favorilere eklendi.")

st.sidebar.header("⭐ Favori Şehirler")
favoriler = db.favorileri_getir()

if len(favoriler) == 0:
    st.sidebar.info("Henüz favori şehir yok.")

for fav in favoriler:
    a, b = st.sidebar.columns([3, 1])
    if a.button(fav, key=f"git_{fav}"):
        goster = fav
    if b.button("❌", key=f"sil_{fav}"):
        db.favori_sil(fav)
        st.rerun()

if goster:
    hava_goster(goster)

st.divider()
st.subheader("Geçmiş Sorgular")

df = db.gecmis_tablo()

if df.empty:
    st.info("Henüz sorgu yapılmadı.")
else:
    st.dataframe(df, use_container_width=True)

    st.subheader("Şehirlerin Sıcaklık Grafiği")
    son_sorgular = df.drop_duplicates("Şehir")

    fig, ax = plt.subplots()
    ax.bar(son_sorgular["Şehir"], son_sorgular["Sıcaklık (°C)"])
    ax.set_ylabel("Sıcaklık (°C)")
    ax.set_title("Son sorgulanan sıcaklıklar")
    plt.xticks(rotation=45)
    st.pyplot(fig)

if st.button("Geçmişi Temizle"):
    db.gecmisi_sil()
    st.rerun()
