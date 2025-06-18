import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import folium
from streamlit_folium import folium_static
from branca.element import Template, MacroElement

# Load dataset
df = pd.read_csv("main_data.csv")
avg_pm25_season_station = pd.read_csv("data_geospasial_pm25_musiman.csv")

# Sidebar untuk memilih stasiun
location = st.sidebar.selectbox("Pilih Stasiun", df['station'].unique())

# Sidebar untuk memilih tahun
year = st.sidebar.selectbox("Pilih Tahun", df['year'].unique())

# Filter data berdasarkan lokasi dan tahun yang dipilih
filtered_df = df[(df['station'] == location) & (df['year'] == year)]

# Tambahkan Info Ringkasan
st.sidebar.subheader("📊 Informasi Data")

if 'PM2.5' in filtered_df.columns:
    avg_pm25 = filtered_df['PM2.5'].mean()
    st.sidebar.metric("Rata-rata PM2.5", f"{avg_pm25:.2f} µg/m³")

# Dashboard Header
st.title("Dashboard Polusi Udara :cloud:")
st.subheader(f"Analisis untuk Stasiun: {location}, Tahun: {year}")

# ========== 1. Tren PM2.5 dari waktu ke waktu ==========
st.subheader("📈 Tren PM2.5 dari Waktu ke Waktu")

pollutants = ['PM2.5']
df_yearly_gas = filtered_df.groupby(['station', 'year', 'month'])[pollutants].mean().reset_index()
month_label = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']

fig, ax = plt.subplots(figsize=(10, 5))
sns.set(style="ticks")
sns.lineplot(x='month', y='PM2.5', data=df_yearly_gas, marker='s', palette='coolwarm', ax=ax)
ax.set_title(f'Tren Bulanan PM2.5 di Stasiun {location} pada Tahun {year}', fontsize=12)
ax.set_xlabel('Bulan', fontsize=10)
ax.set_ylabel('PM2.5 (µg/m³)', fontsize=10)
ax.set_xticks(range(1, 13))
ax.set_xticklabels(month_label, rotation=45)
plt.tight_layout()
st.pyplot(fig)

selected_station = filtered_df['station'].unique()[0]
max_pm25 = df_yearly_gas['PM2.5'].max()
min_pm25 = df_yearly_gas['PM2.5'].min()
max_month = df_yearly_gas.loc[df_yearly_gas['PM2.5'].idxmax(), 'month']
min_month = df_yearly_gas.loc[df_yearly_gas['PM2.5'].idxmin(), 'month']

st.markdown(f"""
Visualisasi ini menampilkan tren bulanan PM2.5 di Stasiun **{selected_station}** pada tahun **{year}** dari Januari hingga Desember.  

### 🔍 **Insight**  
- **Konsentrasi PM2.5 tertinggi** terjadi pada bulan **{month_label[max_month - 1]}** dengan nilai **{max_pm25:.2f} µg/m³**, dan terendah pada bulan **{month_label[min_month - 1]}** dengan nilai **{min_pm25:.2f} µg/m³**.
""")

# ========== 2. Rata-rata PM2.5 per Stasiun ==========
st.subheader("📊 Rata-rata PM2.5 di Berbagai Stasiun")

pm25_mean_per_station = df[df['year'] == year].groupby('station')['PM2.5'].mean()
stations_sorted = pm25_mean_per_station.sort_values(ascending=False)

plt.figure(figsize=(12, 6))
sns.set(style="whitegrid")
sns.barplot(x=stations_sorted.index, y=stations_sorted.values, palette='coolwarm')
plt.title(f'Rata-rata PM2.5 per Stasiun pada Tahun {year}', fontsize=14)
plt.xlabel('Stasiun', fontsize=12)
plt.ylabel('Rata-rata PM2.5 (µg/m³)', fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(plt)

st.markdown(f"""
Visualisasi ini menampilkan rata-rata PM2.5 yang dihitung per stasiun pada tahun **{year}**, memberikan gambaran umum tentang tingkat polusi udara di setiap lokasi.

### 🔍 **Insight**  
- **Stasiun dengan Polusi Tertinggi:** Stasiun **{stations_sorted.index[0]}** memiliki rata-rata PM2.5 tertinggi sebesar **{stations_sorted.values[0]:.2f} µg/m³**.
- **Stasiun dengan Polusi Terendah:** Stasiun **{stations_sorted.index[-1]}** memiliki rata-rata PM2.5 terendah sebesar **{stations_sorted.values[-1]:.2f} µg/m³**.
""")


# ========== 3. Pengaruh Suhu dan Kelembapan terhadap PM2.5 ==========
st.subheader("🌡️ Pengaruh Suhu dan Kelembapan terhadap PM2.5")
fig, ax = plt.subplots(1, 2, figsize=(14, 6))

# Scatterplot Suhu vs PM2.5
st.markdown(f"""
📈 **Pola Persebaran PM2.5 terhadap Suhu dan Kelembapan**
""")

if 'TEMP' in filtered_df.columns and 'PM2.5' in filtered_df.columns:
    sns.scatterplot(x='TEMP', y='PM2.5', data=filtered_df, ax=ax[0], color='blue')
    ax[0].set_title(f"Pengaruh Suhu terhadap PM2.5 ({location}, {year})")
    ax[0].set_xlabel("Suhu (°C)")
    ax[0].set_ylabel("PM2.5 (µg/m³)")

# Scatterplot Kelembapan vs PM2.5
if 'DEWP' in filtered_df.columns and 'PM2.5' in filtered_df.columns:
    sns.scatterplot(x='DEWP', y='PM2.5', data=filtered_df, ax=ax[1], color='green')
    ax[1].set_title(f"Pengaruh Kelembapan terhadap PM2.5 ({location}, {year})")
    ax[1].set_xlabel("Kelembapan (°C)")
    ax[1].set_ylabel("PM2.5 (µg/m³)")

st.pyplot(fig)

# Hitung korelasi
corr_temp = filtered_df[['TEMP', 'PM2.5']].corr().iloc[0, 1]
corr_dewp = filtered_df[['DEWP', 'PM2.5']].corr().iloc[0, 1]

# Interpretasi korelasi
def interpret_corr(corr, var_name):
    abs_corr = abs(corr)
    if abs_corr > 0.7:
        strength = "sangat kuat"
    elif abs_corr > 0.4:
        strength = "kuat"
    elif abs_corr > 0.2:
        strength = "cukup"
    elif abs_corr > 0.1:
        strength = "lemah"
    else:
        strength = "sangat lemah atau tidak ada"

    direction = "positif" if corr > 0 else "negatif"
    trend = "ikut meningkat" if corr > 0 else "menurun"

    signif = "tidak signifikan" if abs_corr <= 0.2 else "mungkin signifikan"

    return (
        f"Korelasi antara **{var_name}** dan PM2.5 adalah **{direction}** "
        f"dengan kekuatan **{strength}** (**{corr:.2f}**), "
        f"yang menunjukkan hubungan {signif}. "
        f"Secara umum, titik data tersebar **{('acak' if abs_corr < 0.2 else 'sedikit membentuk pola')}**, "
        f"menandakan bahwa saat {var_name.lower()} meningkat, PM2.5 cenderung {trend}."
    )
    
# Nilai suhu dan kelembapan dinamis
temp_min = filtered_df['TEMP'].min()
temp_max = filtered_df['TEMP'].max()
temp_threshold = 25  # nilai ambang yang akan kita bandingkan (bisa juga median)

dewp_min = filtered_df['DEWP'].min()
dewp_max = filtered_df['DEWP'].max()
dewp_range_high_pm = filtered_df.loc[filtered_df['PM2.5'] > 400, 'DEWP']

# Dapatkan rentang kelembapan saat PM2.5 tinggi (>400), jika ada
if not dewp_range_high_pm.empty:
    dewp_high_min = dewp_range_high_pm.min()
    dewp_high_max = dewp_range_high_pm.max()
    dewp_high_str = f"{dewp_high_min:.1f}–{dewp_high_max:.1f}°C"
else:
    dewp_high_str = "-"
    
st.markdown(f"""
Visualisasi ini menunjukan pola persebaran konsentrasi PM2.5 dengan suhu (**TEMP**) dan kelembapan (**DEWP**) di Stasiun **{location}** pada tahun **{year}**.

### 🔍 **Insight**
- **PM2.5 terhadap Suhu (TEMP):**  
  Suhu berada dalam rentang **{temp_min:.1f}°C hingga {temp_max:.1f}°C**. PM2.5 tampak cenderung **lebih tinggi pada suhu rendah hingga sedang**, dan **menurun saat suhu melebihi sekitar {temp_threshold}°C**.

- **PM2.5 terhadap Kelembapan (DEWP):**  
  Kelembapan berkisar antara **{dewp_min:.1f}°C hingga {dewp_max:.1f}°C**. PM2.5 terlihat **cenderung meningkat saat kelembapan naik**, dan **PM2.5 sangat tinggi (>400 µg/m³)** paling sering muncul pada rentang kelembapan **{dewp_high_str}**.  
""")
    
# Heatmap korelasi PM2.5, suhu, dan kelembapan
st.markdown("🔥 Heatmap Korelasi antara PM2.5 dengan suhu dan kelembapan:")

fig2, ax2 = plt.subplots(figsize=(8, 4))
weather_vars = ['PM2.5', 'TEMP', 'DEWP']
weather_corr = filtered_df[[col for col in weather_vars if col in filtered_df.columns]].corr()

# Format korelasi untuk heatmap
corr_format = ".2f"

# Tampilkan heatmap dengan warna simetris (-1 s.d. 1)
sns.heatmap(
    weather_corr,
    annot=True,
    fmt=corr_format,
    cmap='coolwarm',
    vmin=-1, vmax=1, center=0,  # ⬅️ Tambahan penting untuk menjaga skala warna tetap simetris
    ax=ax2
)
ax2.set_title(f"Pengaruh Kelembapan terhadap PM2.5 ({location}, {year})")
st.pyplot(fig2)


# Insight dengan format konsisten
st.markdown(f"""
Visualisasi ini menunjukkan korelasi antara suhu, kelembapan, dan kadar PM2.5 di Stasiun **{location}** pada tahun **{year}**.

### 🔍 **Insight**  

**Korelasi PM2.5 dengan Suhu (TEMP): {format(corr_temp, corr_format)}**  
- Nilai korelasi negatif ini menunjukkan bahwa **saat suhu meningkat, kadar PM2.5 cenderung menurun**.

**Korelasi PM2.5 dengan Kelembapan (DEWP): {format(corr_dewp, corr_format)}**  
- Nilai korelasi positif ini menunjukkan bahwa **ketika kelembapan meningkat, kadar PM2.5 juga cenderung meningkat**.
""")


# ========== 4. Geospasial PM2.5 per Musim ==========

st.subheader("🗺️ Visualisasi Geospasial PM2.5 per Musim")

# Koordinat stasiun
station_locations = {
    'Aotizhongxin': [39.909, 116.397],
    'Changping': [40.218, 116.231],
    'Dingling': [40.292, 116.225],
    'Dongsi': [39.929, 116.417],
    'Guanyuan': [39.933, 116.362],
    'Gucheng': [39.914, 116.188],
    'Huairou': [40.364, 116.631],
    'Nongzhanguan': [39.933, 116.470],
    'Shunyi': [40.126, 116.655],
    'Tiantan': [39.876, 116.417],
    'Wanliu': [39.999, 116.288],
    'Wanshouxigong': [39.882, 116.340],
}

# Ikon musim
musim_icons = {
    'Musim Dingin': 'asterisk',
    'Musim Semi': 'leaf',
    'Musim Panas': 'sun',
    'Musim Gugur': 'tree',
}

# Fungsi kategorisasi warna untuk folium
def categorize_color(pm25):
    if pm25 < 70:
        return 'green'
    elif pm25 < 85:
        return 'orange'
    else:
        return 'red'

# Fungsi kategori teks
def get_pm25_label(pm25):
    if pm25 < 70:
        return 'Sedang'
    elif pm25 < 85:
        return 'Tinggi'
    else:
        return 'Sangat Tinggi'

# Pilih musim dari UI
musim_terpilih = st.radio("Pilih Musim:", list(musim_icons.keys()), horizontal=True)

# Buat peta folium
m = folium.Map(location=[39.9042, 116.4074], zoom_start=10, tiles="CartoDB positron")

# Filter data berdasarkan musim
musim_data = avg_pm25_season_station[avg_pm25_season_station['Musim'] == musim_terpilih].copy()
musim_data['lat'] = musim_data['station'].map(lambda x: station_locations.get(x, [None, None])[0])
musim_data['lon'] = musim_data['station'].map(lambda x: station_locations.get(x, [None, None])[1])

# Tambahkan marker ke peta
for _, row in musim_data.iterrows():
    if pd.isna(row['lat']) or pd.isna(row['lon']):
        continue
    color = categorize_color(row['PM2.5'])          # ⬅️ warna sesuai PM2.5
    kategori = get_pm25_label(row['PM2.5'])         # ⬅️ teks label
    icon_name = musim_icons[musim_terpilih]

    popup_html = f"""
    <b>Stasiun:</b> {row['station']}<br>
    <b>Musim:</b> {musim_terpilih}<br>
    <b>PM2.5 Rata-rata:</b> {row['PM2.5']:.2f} µg/m³<br>
    <b>Kategori:</b> {kategori}
    """

    folium.Marker(
        location=[row['lat'], row['lon']],
        popup=folium.Popup(popup_html, max_width=250),
        tooltip=f"{row['station']} | {row['PM2.5']:.1f} µg/m³",
        icon=folium.Icon(color=color, icon=icon_name, prefix='fa')
    ).add_to(m)

# Legenda peta
legend_html = """
{% macro html(this, kwargs) %}
<div style="
    position: fixed; 
    bottom: 50px; 
    left: 50px; 
    width: 240px;
    background-color: white; 
    border: 2px solid grey; 
    z-index: 9999;
    font-size: 14px; 
    padding: 12px; 
    box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
    border-radius: 8px; 
    line-height: 1.5;">
<b>Legenda Kategori PM2.5</b><br>
<i class="fa fa-map-marker fa-lg" style="color:green"></i> Sedang (&lt; 70)<br>
<i class="fa fa-map-marker fa-lg" style="color:orange"></i> Tinggi (70–85)<br>
<i class="fa fa-map-marker fa-lg" style="color:red"></i> Sangat Tinggi (&gt; 85)<br>
</div>
{% endmacro %}
"""

legend = MacroElement()
legend._template = Template(legend_html)
m.get_root().add_child(legend)

# Tampilkan peta
folium_static(m)

# Statistik dan Insight
top3 = musim_data.sort_values(by='PM2.5', ascending=False).head(3)
mean_musim = musim_data['PM2.5'].mean()
max_musim = musim_data['PM2.5'].max()
min_musim = musim_data['PM2.5'].min()

st.markdown(f"""
### 🔍 **Insight: {musim_terpilih}**

- Rata-rata PM2.5 pada musim ini adalah **{mean_musim:.2f} µg/m³**
- Stasiun dengan nilai PM2.5 tertinggi:
  1. **{top3.iloc[0]['station']}**: {top3.iloc[0]['PM2.5']:.2f} µg/m³  
  2. **{top3.iloc[1]['station']}**: {top3.iloc[1]['PM2.5']:.2f} µg/m³  
  3. **{top3.iloc[2]['station']}**: {top3.iloc[2]['PM2.5']:.2f} µg/m³
- PM2.5 tertinggi mencapai **{max_musim:.2f} µg/m³**, sedangkan yang terendah adalah **{min_musim:.2f} µg/m³**
""")


# ========== 5. Distribusi Kategori PM2.5 per Stasiun per Musim ==========

st.subheader(f"🏭 Distribusi Kategori PM2.5 per Stasiun pada {musim_terpilih}")

# Filter data musim terpilih
season_df = avg_pm25_season_station[avg_pm25_season_station['Musim'] == musim_terpilih].copy()

# Pastikan kategori dihitung ulang
def categorize_pm25(pm25):
    if pm25 < 65:
        return 'Rendah'
    elif pm25 < 75:
        return 'Sedang'
    else:
        return 'Tinggi'

season_df['Kategori_PM2.5'] = season_df['PM2.5'].apply(categorize_pm25)

# Plot
fig_kat, ax_kat = plt.subplots(figsize=(8, 5))
sns.countplot(
    data=season_df,
    x='Kategori_PM2.5',
    order=['Rendah', 'Sedang', 'Tinggi'],
    palette={'Rendah': 'green', 'Sedang': 'orange', 'Tinggi': 'red'},
    ax=ax_kat
)
ax_kat.set_title(f'Distribusi Kategori Rata-rata PM2.5 pada {musim_terpilih}')
ax_kat.set_xlabel('Kategori PM2.5')
ax_kat.set_ylabel('Jumlah Stasiun')
ax_kat.grid(axis='y', linestyle='--', alpha=0.6)

st.pyplot(fig_kat)

# Insight
counts = season_df['Kategori_PM2.5'].value_counts()
st.markdown(f"""
Visualisasi ini menampilkan distribusi kategori rata-rata PM2.5 pada musim **{musim_terpilih}**, yang konsisten dengan warna dan kategori pada peta geospasial.

### 🔍  **Insight Kategori PM2.5 di {musim_terpilih}**

- Jumlah stasiun dengan kategori **Rendah**: {counts.get('Rendah', 0)}  
- Jumlah stasiun dengan kategori **Sedang**: {counts.get('Sedang', 0)}  
- Jumlah stasiun dengan kategori **Tinggi**: {counts.get('Tinggi', 0)}  
""")
