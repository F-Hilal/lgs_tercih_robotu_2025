
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
import streamlit.components.v1 as components

html_table = eslesen_okullar[["İLÇE", "OKUL ADI", "2022", "2023", "2024", "2025 Tahmin", "ALAN", "OKUL TÜRÜ"]].to_html(index=False, escape=False)

wrapped_html = f"""
<style>
    .custom-table-container {{
        max-width: 1100px;
        margin: auto;
        overflow-x: auto;
    }}
    table {{
        width: 100%;
        table-layout: fixed;
        border-collapse: collapse;
        font-size: 14px;
    }}
    th, td {{
        border: 1px solid #ccc;
        padding: 8px;
        text-align: center;
        vertical-align: middle;
        word-wrap: break-word;
        white-space: normal;
    }}
    th {{
        background-color: #f0f2f6;
        font-weight: bold;
    }}
    tr:nth-child(even) {{
        background-color: #f9f9f9;
    }}

    /* Sütun genişlikleri */
    td:nth-child(1), th:nth-child(1) {{ width: 120px; text-align: left; }}
    td:nth-child(2), th:nth-child(2) {{ max-width: 250px; text-align: left; }}
    td:nth-child(7), th:nth-child(7) {{ width: 120px; text-align: left; }}
    td:nth-child(8), th:nth-child(8) {{ width: 120px; text-align: left; }}

    td:nth-child(3), td:nth-child(4), td:nth-child(5), td:nth-child(6),
    th:nth-child(3), th:nth-child(4), th:nth-child(5), th:nth-child(6) {{
        width: 60px;
    }}
</style>

<div class="custom-table-container">
    {html_table}
</div>
"""
st.markdown(wrapped_html, unsafe_allow_html=True)

# Excel olarak indirme
import io

def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Tercih Listesi")
    return output.getvalue()

excel_data = convert_df_to_excel(eslesen_okullar)

st.download_button(
    label="📥 Listeyi Excel Olarak İndir",
    data=excel_data,
    file_name="tercih_listesi_2025.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
