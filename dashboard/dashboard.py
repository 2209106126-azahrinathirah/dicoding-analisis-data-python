import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='darkgrid')

# Load dataset
url = "https://raw.githubusercontent.com/2209106126-azahrinathirah/dicoding-analisis-data-python/main/dashboard/main_data.csv"
df = pd.read_csv(url)

# Pastikan kolom datetime dalam format yang benar
df['datetime'] = pd.to_datetime(df['datetime'])

# Ambil rentang tanggal dari dataset
date_min, date_max = df['datetime'].min(), df['datetime'].max()

# Sidebar untuk memilih stasiun dan rentang waktu
location = st.sidebar.selectbox("Pilih Stasiun", df['station'].unique())

# Pilih rentang waktu dengan Streamlit date_input
start_date, end_date = st.sidebar.date_input("Pilih Rentang Waktu", [date_min.date(), date_max.date()], date_min.date(), date_max.date())

# Konversi start_date dan end_date ke datetime64
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Filter data sesuai input pengguna
filtered_df = df[(df['station'] == location) & (df['datetime'].between(start_date, end_date))]

# **Tambahkan Info Ringkasan**
st.sidebar.subheader("📊 Informasi Data")
st.sidebar.metric("Total Pengukuran", len(filtered_df))
if 'PM2.5' in filtered_df.columns:
    st.sidebar.metric("Rata-rata PM2.5", f"{filtered_df['PM2.5'].mean():.2f} µg/m³")

# Dashboard Header
st.title("Dashboard Polusi Udara :cloud:")
st.subheader(f"Analisis untuk Stasiun: {location}")
st.markdown(f"📅 **Rentang Waktu:** {start_date.date()} - {end_date.date()}")

# 1. **Tren PM2.5 dari waktu ke waktu**
st.subheader("📈 Tren PM2.5 dari Waktu ke Waktu")
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(filtered_df['datetime'], filtered_df['PM2.5'], marker='o', linestyle='-', color='red')
ax.set_xlabel("Tanggal")
ax.set_ylabel("PM2.5 (µg/m³)")
ax.set_title("Tren PM2.5 dari Waktu ke Waktu")
st.pyplot(fig)
st.markdown("🔹 Grafik ini menunjukkan bagaimana tingkat PM2.5 berubah seiring waktu.")

# 2. **Variasi PM2.5 berdasarkan polutan utama**
st.subheader("🔬 Variasi PM2.5 Berdasarkan Polutan Utama")
fig, ax = plt.subplots(figsize=(12, 6))
polutan = ['SO2', 'NO2', 'O3', 'CO']

# Pastikan hanya mengambil kolom yang ada di dataset
filtered_corr = filtered_df[[col for col in polutan + ['PM2.5'] if col in filtered_df.columns]]

sns.heatmap(filtered_corr.corr(), annot=True, cmap='coolwarm', ax=ax)
ax.set_title("Korelasi PM2.5 dengan Polutan Lain")
st.pyplot(fig)
st.markdown("🔹 Korelasi menunjukkan bagaimana hubungan antara PM2.5 dengan polutan lainnya.")

# 3. **Pengaruh Suhu dan Kelembapan terhadap PM2.5**
st.subheader("🌡️ Pengaruh Suhu dan Kelembapan terhadap PM2.5")
fig, ax = plt.subplots(1, 2, figsize=(14, 6))

# Pastikan kolom TEMP dan DEWP ada di dataset
if 'TEMP' in filtered_df.columns and 'PM2.5' in filtered_df.columns:
    sns.scatterplot(x=filtered_df['TEMP'], y=filtered_df['PM2.5'], ax=ax[0], color='blue')
    ax[0].set_title("Pengaruh Suhu terhadap PM2.5")
    ax[0].set_xlabel("Suhu (°C)")
    ax[0].set_ylabel("PM2.5 (µg/m³)")

if 'DEWP' in filtered_df.columns and 'PM2.5' in filtered_df.columns:
    sns.scatterplot(x=filtered_df['DEWP'], y=filtered_df['PM2.5'], ax=ax[1], color='green')
    ax[1].set_title("Pengaruh Kelembapan terhadap PM2.5")
    ax[1].set_xlabel("Kelembapan (°C)")
    ax[1].set_ylabel("PM2.5 (µg/m³)")

st.pyplot(fig)
st.markdown("🔹 Scatterplot ini memperlihatkan bagaimana suhu dan kelembapan mempengaruhi kadar PM2.5.")

st.caption("📌 **Sumber Data:** Pengukuran Polusi Udara")
