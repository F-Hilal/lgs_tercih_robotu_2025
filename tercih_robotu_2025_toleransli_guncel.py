
import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="LGS Tercih Robotu 2025", layout="wide")

st.title("🎯 LGS Tercih Robotu 2025")

# Veri yükleme
df = pd.read_csv("veri.csv.csv", encoding="ISO-8859-9", sep=";")

# 2025 tahmini (2022, 2023, 2024'e göre)
df = df.dropna(subset=["2022", "2023", "2024"])
def tahmin_et(satir):
    yillar = [[1], [2], [3]]  # 2022, 2023, 2024
    yuzdelikler = [satir["2022"], satir["2023"], satir["2024"]]
    
    model = LinearRegression()
    model.fit(yillar, yuzdelikler)
    tahmin = model.predict([[4]])[0]  # 2025 için yıl = 4
    return round(tahmin, 2)

df["2025 Tahmin"] = df.apply(tahmin_et, axis=1)

# Filtreler
ilceler = sorted(df["İLÇE"].dropna().unique())
alanlar = sorted(df["ALAN"].dropna().unique())

secili_ilceler = st.multiselect("📍 İlçeleri Seçin", options=ilceler, default=ilceler)
secili_alanlar = st.multiselect("🏫 Alanları Seçin", options=alanlar, default=alanlar)

# Filtreleme işlemi
df_filtreli = df[
    (df["İLÇE"].isin(secili_ilceler)) &
    (df["ALAN"].isin(secili_alanlar))
]

# Kullanıcının yüzdelik dilimi ve tolerans girişi
st.sidebar.header("🎯 Kendi Bilgilerin")
yuzdelik = st.sidebar.number_input("📌 Yüzdelik Diliminiz (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.1)
tolerans = st.sidebar.slider("🎯 Tolerans Aralığı (±%)", min_value=0.0, max_value=10.0, value=1.0, step=0.1)

# Tahmini yüzdelik aralığına göre filtreleme
alt_sinir = max(0, yuzdelik - tolerans)
ust_sinir = min(100, yuzdelik + tolerans)

eslesen_okullar = df_filtreli[
    (df_filtreli["2025 Tahmin"] >= alt_sinir) &
    (df_filtreli["2025 Tahmin"] <= ust_sinir)
].sort_values("2025 Tahmin")

# Sonuçları göster
st.subheader(f"📋 {alt_sinir:.2f}–{ust_sinir:.2f} arası uygun okullar")
st.dataframe(eslesen_okullar[["OKUL ADI", "İLÇE", "ALAN", "2022", "2023", "2024", "2025 Tahmin"]])
