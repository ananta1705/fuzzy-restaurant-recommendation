import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

# ============================================
# STEP 1: DATASET LENGKAP 38 PROVINSI
# ============================================
data = {
    'PROVINSI': [
        'Aceh', 'Sumatera Utara', 'Sumatera Barat', 'Riau', 'Jambi', 'Sumatera Selatan',
        'Bengkulu', 'Lampung', 'Kep. Bangka Belitung', 'Kepulauan Riau', 'DKI Jakarta',
        'Jawa Barat', 'Jawa Tengah', 'DI Yogyakarta', 'Jawa Timur', 'Banten', 'Bali',
        'Nusa Tenggara Barat', 'Nusa Tenggara Timur', 'Kalimantan Barat', 'Kalimantan Tengah',
        'Kalimantan Selatan', 'Kalimantan Timur', 'Kalimantan Utara', 'Sulawesi Utara',
        'Sulawesi Tengah', 'Sulawesi Selatan', 'Sulawesi Tenggara', 'Gorontalo', 'Sulawesi Barat',
        'Maluku', 'Maluku Utara', 'Papua Selatan', 'Papua Tengah', 'Papua Pegunungan',
        'Papua Barat Daya', 'Papua Barat', 'Papua'
    ],
    'STUNTING': [
        28.6, 22.0, 24.9, 20.1, 17.1, 15.9, 18.8, 15.9, 20.1, 15.0, 17.3, 15.9, 17.1, 17.4, 
        14.7, 21.1, 8.7, 29.8, 37.0, 27.8, 26.9, 24.6, 23.9, 22.1, 20.5, 28.2, 27.2, 27.7, 
        23.8, 33.8, 26.1, 26.1, 25.0, 30.0, 35.0, 24.0, 30.0, 34.6
    ],
    'KEMISKINAN (%)': [
        12.64, 7.19, 5.42, 6.36, 7.26, 10.51, 12.52, 10.62, 5.08, 4.78, 4.14, 7.08, 9.58, 
        10.40, 9.56, 5.70, 3.80, 11.91, 19.02, 6.70, 5.20, 4.30, 6.10, 6.50, 7.20, 12.30, 
        8.60, 11.20, 15.10, 11.50, 15.90, 6.40, 18.0, 20.0, 25.0, 17.0, 21.0, 26.0
    ],
    'PDRB_PER_KAPITA': [
        43782, 73575, 57083, 165350, 86775, 75132, 49233, 51387, 70193, 161424, 344383, 
        56082, 47970, 51486, 75770, 70276, 67318, 32282, 24303, 52000, 65000, 62000, 
        230000, 180000, 68000, 95000, 78000, 63000, 45000, 42000, 31000, 48000, 35000, 
        38000, 28000, 55000, 62000, 58000
    ]
}
df = pd.DataFrame(data)

# ============================================
# STEP 2: METODE ELBOW (K=1, K=3, K=4)
# ============================================
# Deret angka KWCSS yang diberikan (diurutkan dari terbesar)
kwcss_values = [
    834023808100, 97074870590, 63204170461, 58180003133, 18058104624, 
    13585591880, 3700633571, 2631784742, 1557638151, 72651958
]
k_range = range(1, len(kwcss_values) + 1)

plt.figure(figsize=(10, 5))
plt.plot(k_range, kwcss_values, marker='o', linestyle='-', color='red', linewidth=2)
plt.title('Grafik Metode Elbow (Analisis Nilai KWCSS)', fontsize=14)
plt.xlabel('Jumlah Cluster (K)', fontsize=12)
plt.ylabel('Nilai WCSS / Inertia', fontsize=12)
plt.xticks(k_range)
plt.grid(True, alpha=0.3)

# Menampilkan keterangan K=1, K=3, dan K=4 dalam warna hitam
plt.text(1.2, kwcss_values[0], 'K=1: Error Sangat Tinggi', fontsize=10, color='black')
plt.text(3.2, kwcss_values[2], 'K=3: Siku 1', fontsize=10, color='black', fontweight='bold')
plt.text(4.2, kwcss_values[3], 'K=4: Siku 2 (Optimal)', fontsize=10, color='black', fontweight='bold')

plt.show()

# ============================================
# STEP 3: K-MEANS CLUSTERING (K=4)
# ============================================
features = ['STUNTING', 'KEMISKINAN (%)', 'PDRB_PER_KAPITA']
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(df[features])

# Menggunakan K=4 sesuai titik optimal pada grafik elbow
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
df['Cluster'] = kmeans.fit_predict(X_scaled)

# Penyesuaian Kategori (Urutan 1-4 berdasarkan rata-rata stunting)
cluster_means = df.groupby('Cluster')['STUNTING'].mean().sort_values()
mapping = {
    cluster_means.index[0]: 'Rendah', 
    cluster_means.index[1]: 'Sedang', 
    cluster_means.index[2]: 'Tinggi',
    cluster_means.index[3]: 'Sangat Tinggi'
}
df['Kategori'] = df['Cluster'].map(mapping)

# ============================================
# STEP 4: VISUALISASI SCATTER BUBBLE
# ============================================
df['hover_text'] = (
    "<b>" + df['PROVINSI'] + "</b><br><br>" +
    "Kategori=" + df['Kategori'] + "<br>" +
    "Tingkat Kemiskinan (%)=" + df['KEMISKINAN (%)'].astype(str) + "<br>" +
    "Prevalensi Stunting (%)=" + df['STUNTING'].astype(str) + "<br>" +
    "PDRB_PER_KAPITA=" + df['PDRB_PER_KAPITA'].apply(lambda x: "{:,}".format(x))
)

fig = px.scatter(
    df, x="KEMISKINAN (%)", y="STUNTING", size="STUNTING", color="Kategori",
    text="PROVINSI", title="Visualisasi Cluster Stunting 38 Provinsi (K=4)",
    color_discrete_map={
        "Sangat Tinggi": "#8B0000", # Merah Tua
        "Tinggi": "#E74C3C",        # Merah
        "Sedang": "#F39C12",        # Oranye
        "Rendah": "#27AE60"         # Hijau
    },
    template="plotly_white"
)

fig.update_traces(
    customdata=df['hover_text'], hovertemplate="%{customdata}<extra></extra>",
    textposition='top center', hoverlabel=dict(font_color="white")
)

fig.show()