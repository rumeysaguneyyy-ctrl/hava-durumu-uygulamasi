import streamlit as st
import matplotlib.pyplot as plt
from hava import HavaServisi
from veritabani import Veritabani

hava_servisi = HavaServisi()
db = Veritabani()

st.title("Hava Durumu Uygulaması")

sehir = st.text_input("Şehir adı", "Istanbul")

if st.button("Hava Durumunu Getir"):
    sonuc = hava_servisi.sehir_hava(sehir)

    if sonuc is None:
        st.error("Şehir bulunamadı, tekrar dene.")
    else:
        sicaklik, ruzgar = sonuc
        db.sorgu_kaydet(sehir, sicaklik, ruzgar)

        st.subheader(sehir)
        sol, sag = st.columns(2)
        sol.metric("Sıcaklık", f"{sicaklik} °C")
        sag.metric("Rüzgar", f"{ruzgar} km/s")

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