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


# ========== 3. Scatter Plot PM2.5 vs Polutan ==========
st.subheader("📈 Hubungan PM2.5 dengan CO, NO2, dan SO2 (Tahun per Tahun)")

def plot_pm25_scatter_polutans(filtered_df, location, year):
    df_station = filtered_df.copy()

    # Pastikan kolom tanggal dan tahun tersedia
    if 'date' not in df_station.columns and {'year', 'month', 'day'}.issubset(df_station.columns):
        df_station['date'] = pd.to_datetime(df_station[['year', 'month', 'day']], errors='coerce')
    if 'year' not in df_station.columns:
        df_station['year'] = df_station['date'].dt.year

    polutans = ['CO', 'NO2', 'SO2']
    colors = ['#66c2a5', '#fc8d62', '#8da0cb']
    line_colors = ['#82E0AA', '#F1948A', '#5DADE2']

    insight_list = []

    for i, polutan in enumerate(polutans):
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.set(style="whitegrid")

        if polutan in df_station.columns and 'PM2.5' in df_station.columns:
            df_filtered = df_station[[polutan, 'PM2.5']].dropna()

            if not df_filtered.empty and len(df_filtered) > 10:
                sns.regplot(
                    x=polutan, y='PM2.5',
                    data=df_filtered,
                    ax=ax,
                    scatter_kws={'alpha': 0.3, 's': 25},
                    line_kws={'color': line_colors[i]},
                    color=colors[i],
                    ci=95
                )
                ax.set_ylim(0, df_filtered['PM2.5'].max() + 50)
                ax.set_title(f"{polutan} vs PM2.5 di {location} ({year})", fontsize=13)
                ax.set_xlabel(polutan)
                ax.set_ylabel("PM2.5 (µg/m³)")

                # Simpan insight
                korelasi = df_filtered.corr().loc['PM2.5', polutan]
                if korelasi > 0.7:
                    pola = "terlihat pola linear yang kuat"
                elif korelasi > 0.5:
                    pola = "terlihat kecenderungan meningkat seiring meningkatnya polutan"
                elif korelasi > 0.3:
                    pola = "hubungan cenderung menyebar tapi masih menunjukkan arah positif"
                else:
                    pola = "penyebaran titik sangat acak dan tidak menunjukkan arah yang jelas"

                pengaruh = "berpengaruh cukup besar" if korelasi > 0.5 else "tidak terlalu berdampak"
                insight_list.append(
                    f"- Untuk **{polutan}**, {pola}. Hal ini menunjukkan bahwa perubahan nilai {polutan} {pengaruh} terhadap PM2.5."
                )
            else:
                ax.text(0.5, 0.5, "Data tidak cukup", ha='center', va='center')
                ax.set_axis_off()
                insight_list.append(f"- Data untuk **{polutan}** tidak cukup untuk dianalisis secara visual.")

        st.pyplot(fig)

    # Insight ditampilkan SETELAH SEMUA grafik
    st.markdown(f"""
### 🔍 **Insight**

Berdasarkan sebaran titik-titik pada grafik dan arah garis regresi linear, berikut adalah pengamatan untuk stasiun **{location}** pada tahun **{year}**:
""")
    for item in insight_list:
        st.markdown(item)


# Jalankan jika data tersedia
if not filtered_df.empty:
    plot_pm25_scatter_polutans(filtered_df, location, year)
else:
    st.warning("Silakan pilih stasiun dan tahun untuk melihat hubungan PM2.5 dan polutan.")




# ========== 4. Korelasi PM2.5 dengan Polutan Lain ==========
st.subheader("📊 Korelasi PM2.5 dengan Polutan Lain (CO, NO2, SO2)")

def plot_correlation_pm25_with_polutants(filtered_df, location, year):
    df_corr = filtered_df[['PM2.5', 'CO', 'NO2', 'SO2']].dropna()

    if df_corr.empty or df_corr.shape[0] < 3:
        st.warning("Data tidak cukup untuk menghitung korelasi.")
        return

    corr_matrix = df_corr.corr()
    data_korelasi = {
        'Polutan': ['CO', 'NO2', 'SO2'],
        'Korelasi dengan PM2.5': [
            corr_matrix.loc['PM2.5', 'CO'],
            corr_matrix.loc['PM2.5', 'NO2'],
            corr_matrix.loc['PM2.5', 'SO2']
        ]
    }
    df_korelasi = pd.DataFrame(data_korelasi)

    # Buat visualisasi batang
    fig, ax = plt.subplots(figsize=(5, 5))
    sns.barplot(data=df_korelasi, x='Polutan', y='Korelasi dengan PM2.5', palette='Set2', ax=ax)
    ax.set_ylim(0, 1)
    ax.set_title(f"Korelasi PM2.5 dengan Polutan Lain ({location}, {year})")
    ax.set_ylabel("Nilai Korelasi")

    # Tambah label nilai korelasi
    for i, val in enumerate(df_korelasi['Korelasi dengan PM2.5']):
        ax.text(i, val + 0.02, f"{val:.2f}", ha='center', va='bottom')

    st.pyplot(fig)
    
    st.markdown(f"""
Visualisasi ini menampilkan **nilai korelasi antara PM2.5 dan polutan (CO, NO2, SO2)** di stasiun **{location}** untuk masing-masing tahun.

### 🔍 **Insight**
""")
    for i, row in df_korelasi.iterrows():
        polutan = row['Polutan']
        nilai = row['Korelasi dengan PM2.5']
        if nilai > 0.7:
            kategori = "sangat kuat"
        elif nilai > 0.5:
            kategori = "kuat"
        elif nilai > 0.3:
            kategori = "cukup"
        else:
            kategori = "lemah"

        st.markdown(
            f"- Korelasi antara PM2.5 dan **{polutan}** adalah **{nilai:.2f}** (**{kategori}**), "
            f"menunjukkan bahwa ketika {polutan} meningkat, kemungkinan besar PM2.5 juga ikut meningkat."
        )
        
    
# Jalankan jika data tersedia
if not filtered_df.empty:
    plot_correlation_pm25_with_polutants(filtered_df, location, year)
else:
    st.warning("Silakan pilih stasiun dan tahun untuk menampilkan analisis korelasi.")
    

# ========== 5. Geospasial PM2.5 per Musim ==========

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


# ========== 6. Distribusi Kategori PM2.5 per Stasiun per Musim ==========

st.subheader(f"📊 Distribusi Kategori PM2.5 per Stasiun pada {musim_terpilih}")

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

st.markdown("") 

st.markdown("""
### 🧾 Kesimpulan Analisis

#### 📌 **Conclusion Pertanyaan 1**  
**Bagaimana perubahan tren bulanan konsentrasi PM2.5 di berbagai stasiun pada tahun 2013–2017?**

1. Tiap stasiun menunjukkan tren bulanan PM2.5 yang mirip selama periode 2013–2017:
   - **2013**: Lonjakan pada Maret dan Juni, penurunan pada Juli–September.  
   - **2014**: Penurunan dibanding 2013, dengan lonjakan kecil di Februari.  
   - **2015**: Lonjakan ekstrem di Desember (>160 μg/m³), menjadi puncak tertinggi.  
   - **2016**: Tren menurun namun tetap ada lonjakan di akhir tahun.  
   - **2017**: Data hanya Januari–Februari, tetap menunjukkan kadar tinggi.

2. Stasiun dengan **rata-rata PM2.5 tertinggi**: **Dongsi**, **Nongzhanguan**, **Wanshouxigong**  
   Stasiun dengan **rata-rata PM2.5 terendah**: **Dingling**, **Huairou**, **Changping**

---

#### 📌 **Conclusion Pertanyaan 2**  
**Bagaimana hubungan antara PM2.5 dengan CO, NO₂, dan SO₂ di berbagai stasiun tahun 2013–2017, dan polutan mana yang paling berkorelasi?**


1. **CO dan NO₂** menunjukkan korelasi yang paling kuat dan konsisten terhadap PM2.5.  
2. **SO₂** memiliki hubungan paling lemah, dan korelasinya cenderung menurun dari tahun ke tahun.

---

#### 📌 **Conclusion Pertanyaan 3 (Analisis Lanjutan)**  
**Bagaimana pola spasial konsentrasi PM2.5 berdasarkan musim di seluruh stasiun di Beijing?**

Sebaran spasial musiman di seluruh stasiun menunjukkan bahwa:
- ❄️ **Musim dingin dan semi** memiliki tingkat PM2.5 tertinggi, dengan sebagian besar stasiun pada kategori polusi tinggi.  
- 🌤️ **Musim panas** menunjukkan kualitas udara terbaik, mayoritas stasiun berada pada kategori sedang hingga rendah.  
- 🍂 **Musim gugur** berada di tengah, dengan banyak stasiun dalam kategori tinggi namun tidak separah musim dingin.

---
""")
