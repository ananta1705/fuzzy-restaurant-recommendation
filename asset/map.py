import pandas as pd
import plotly.express as px

# 1. Menyiapkan Data Lengkap 38 Provinsi (Berdasarkan input Anda)
data = {
    'PROVINSI': [
        'Aceh', 'Sumatera Utara', 'Sumatera Barat', 'Riau', 'Jambi', 'Sumatera Selatan',
        'Bengkulu', 'Lampung', 'Kepulauan Bangka Belitung', 'Kepulauan Riau', 'DKI Jakarta',
        'Jawa Barat', 'Jawa Tengah', 'DI Yogyakarta', 'Jawa Timur', 'Banten', 'Bali',
        'Nusa Tenggara Barat', 'Nusa Tenggara Timur', 'Kalimantan Barat', 'Kalimantan Tengah',
        'Kalimantan Selatan', 'Kalimantan Timur', 'Kalimantan Utara', 'Sulawesi Utara',
        'Sulawesi Tengah', 'Sulawesi Selatan', 'Sulawesi Tenggara', 'Gorontalo', 'Sulawesi Barat',
        'Maluku', 'Maluku Utara', 'Papua Barat', 'Papua Barat Daya', 'Papua', 'Papua Selatan',
        'Papua Tengah', 'Papua Pegunungan'
    ],
    'STUNTING': [
        28.6, 22.0, 24.9, 20.1, 17.1, 15.9, 18.8, 15.9, 20.1, 15.0, 17.3, 15.9, 17.1, 17.4,
        14.7, 21.1, 8.7, 29.8, 37.0, 26.8, 22.1, 22.9, 22.2, 17.6, 20.8, 26.1, 23.3, 26.1,
        23.8, 35.4, 28.4, 23.2, 24.6, 30.5, 24.7, 25.8, 32.5, 40.0
    ],
    'KETERANGAN': [
        'Prioritas 1 (Tinggi)', 'Prioritas 2 (Sedang)', 'Prioritas 2 (Sedang)', 'Prioritas 2 (Sedang)', 
        'Prioritas 2 (Sedang)', 'Prioritas 2 (Sedang)', 'Prioritas 2 (Sedang)', 'Prioritas 2 (Sedang)', 
        'Prioritas 2 (Sedang)', 'Prioritas 2 (Sedang)', 'Prioritas 2 (Sedang)', 'Prioritas 3 (Rendah)', 
        'Prioritas 3 (Rendah)', 'Prioritas 2 (Sedang)', 'Prioritas 3 (Rendah)', 'Prioritas 2 (Sedang)', 
        'Prioritas 2 (Sedang)', 'Prioritas 1 (Tinggi)', 'Prioritas 1 (Tinggi)', 'Prioritas 2 (Sedang)', 
        'Prioritas 2 (Sedang)', 'Prioritas 2 (Sedang)', 'Prioritas 2 (Sedang)', 'Prioritas 2 (Sedang)', 
        'Prioritas 2 (Sedang)', 'Prioritas 2 (Sedang)', 'Prioritas 2 (Sedang)', 'Prioritas 2 (Sedang)', 
        'Prioritas 1 (Tinggi)', 'Prioritas 1 (Tinggi)', 'Prioritas 1 (Tinggi)', 'Prioritas 2 (Sedang)', 
        'Prioritas 1 (Tinggi)', 'Prioritas 1 (Tinggi)', 'Prioritas 1 (Tinggi)', 'Prioritas 1 (Tinggi)', 
        'Prioritas 1 (Tinggi)', 'Prioritas 1 (Tinggi)'
    ]
}

df = pd.DataFrame(data)

# 2. GeoJSON Indonesia (Data batas wilayah untuk memetakan nama provinsi)
geojson_url = "https://raw.githubusercontent.com/anshori/geojson-indonesia/master/provinces.geojson"

# 3. Membuat Peta
fig = px.choropleth(
    df,
    geojson=geojson_url,
    locations='PROVINSI',
    featureidkey="properties.NAME_1",
    color='KETERANGAN',
    hover_name='PROVINSI',
    hover_data={'STUNTING': True, 'KETERANGAN': False},
    title='<b>Peta Prioritas Penanganan Stunting Indonesia (38 Provinsi)</b>',
    color_discrete_map={
        'Prioritas 1 (Tinggi)': '#D32F2F', # Merah
        'Prioritas 2 (Sedang)': '#FBC02D', # Kuning
        'Prioritas 3 (Rendah)': '#388E3C'  # Hijau
    }
)

# Simpan peta sebagai gambar statis (memerlukan library kaleido)
# pip install -U kaleido
fig.write_image("peta_stunting_indonesia.png")

print("Peta telah berhasil disimpan dengan nama peta_stunting_indonesia.png")
# Mengatur tampilan peta agar pas ke wilayah Indonesia
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0})

# Menampilkan peta
fig.show()