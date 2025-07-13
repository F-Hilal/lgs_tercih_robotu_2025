
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="LGS Tercih Robotu 2025", layout="wide")
st.title("🎯 LGS Tercih Robotu 2025")

# Veri yükleme
df = pd.read_csv("veri_duzenli_sirali.csv", encoding="utf-8-sig")
for yil in ["2022", "2023", "2024"]:
    df[yil] = pd.to_numeric(df[yil], errors="coerce")

# Tahmin fonksiyonu
def tahmin_et(satir):
    veriler = []
    for i, yil in enumerate(["2022", "2023", "2024"], start=1):
        try:
            deger = float(satir[yil])
            if deger > 0:
                veriler.append((i, deger))
        except:
            continue
    if len(veriler) == 0:
        return np.nan
    elif len(veriler) == 1:
        return round(veriler[0][1], 2)
    else:
        X = np.array([[v[0]] for v in veriler])
        y = np.array([v[1] for v in veriler])
        model = LinearRegression()
        model.fit(X, y)
        tahmin = model.predict([[4]])[0]
        return round(tahmin, 2)

df["2025 Tahmin"] = df.apply(tahmin_et, axis=1)

# Filtreler
ilceler = sorted(df["İLÇE"].dropna().unique())
alanlar = sorted(df["ALAN"].dropna().unique())
okul_turleri = sorted(df["OKUL TÜRÜ"].dropna().unique())

secili_ilceler = st.multiselect("📍 İlçeleri Seçin", options=ilceler, default=ilceler)
secili_alanlar = st.multiselect("🏫 Alanları Seçin", options=alanlar, default=alanlar)
secili_turler = st.multiselect("🏷️ Okul Türünü Seçin", options=okul_turleri, default=okul_turleri)

# Filtreleme işlemi
df_filtreli = df[
    (df["İLÇE"].isin(secili_ilceler)) &
    (df["ALAN"].isin(secili_alanlar)) &
    (df["OKUL TÜRÜ"].isin(secili_turler))
]

# Kullanıcı bilgileri
st.sidebar.header("🎯 Kendi Bilgilerin")
yuzdelik = st.sidebar.number_input("📌 Yüzdelik Diliminiz (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.1)
tolerans = st.sidebar.slider("🎯 Tolerans Aralığı (±%)", min_value=0.0, max_value=10.0, value=1.0, step=0.1)

alt_sinir = max(0, yuzdelik - tolerans)
ust_sinir = min(100, yuzdelik + tolerans)

eslesen_okullar = df_filtreli[
    (df_filtreli["2025 Tahmin"] >= alt_sinir) &
    (df_filtreli["2025 Tahmin"] <= ust_sinir)
].sort_values("2025 Tahmin")

# Bilgilendirme
st.subheader(f"📋 {alt_sinir:.2f}–{ust_sinir:.2f} arası uygun okullar")
st.markdown("ℹ️ Bu analiz geçmiş yıllara dayanarak yapıldığı için 2025 tahminleri için yaklaşık bir güven aralığı verir. Ortalama ±3 puan sapma beklenebilir.")

# Sonuç tablosu
from IPython.core.display import HTML
import streamlit.components.v1 as components

html_table = eslesen_okullar[["İLÇE", "OKUL ADI", "2022", "2023", "2024", "2025 Tahmin", "ALAN", "TÜR"]].to_html(index=False, escape=False)

wrapped_html = f"""
<div style="overflow-x:auto; max-width:100%;">
    <style>
        table {{
            width: 100%;
            table-layout: auto;
            word-wrap: break-word;
            white-space: normal;
            font-size: 14px;
        }}
        th, td {{
            padding: 6px;
            text-align: left;
            vertical-align: top;
        }}
    </style>
    {html_table}
</div>
"""

st.subheader(f"📋 {alt_sinir:.2f}–{ust_sinir:.2f} arası uygun okullar")
st.markdown(wrapped_html, unsafe_allow_html=True)

# Excel olarak indirme
def convert_df_to_excel(df):
    return df.to_csv(index=False).encode("utf-8")

excel_data = convert_df_to_excel(eslesen_okullar)
st.download_button(
    label="📥 Listeyi Excel Olarak İndir",
    data=excel_data,
    file_name="tercih_listesi_2025.csv",
    mime="text/csv"
)
