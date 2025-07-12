
import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="LGS Tercih Robotu 2025", layout="wide")

st.title("🎯 LGS Tercih Robotu 2025")

# Veri yükleme
df = pd.read_csv("veri.csv", encoding="ISO-8859-9", sep=";")

# 2025 tahmini (2022, 2023, 2024'e göre)
df = df.dropna(subset=["2022", "2023", "2024"])
X = df[["2022", "2023", "2024"]]
y = df["2024"]

model = LinearRegression()
model.fit(X, y)
df["2025 Tahmin"] = model.predict(X).round(2)

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

# Tercih yüzdeliği girişi
yuzdelik = st.number_input("📌 Kendi Yüzdelik Diliminizi Girin", min_value=0.0, max_value=100.0, value=5.0, step=0.1)

# Eşleşen okulları filtrele
eslesen_okullar = df_filtreli[df_filtreli["2025 Tahmin"] >= yuzdelik].sort_values("2025 Tahmin")

st.subheader("📋 Uygun Okullar (2025 Tahminine Göre)")
st.dataframe(eslesen_okullar[["OKUL ADI", "İLÇE", "ALAN", "2022", "2023", "2024", "2025 Tahmin"]])
