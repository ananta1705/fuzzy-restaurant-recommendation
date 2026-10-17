# Digital Consumer Interest in Indonesian E-Commerce (2020–2025)

Analisis minat pencarian masyarakat Indonesia terhadap lima platform e-commerce—Shopee, Tokopedia, Lazada, Blibli, dan TikTok Shop—menggunakan indeks Google Trends. Analisis dilakukan dalam dua dimensi: tren waktu bulanan dan pola regional pada 34 provinsi.

> **Catatan interpretasi:** Google Trends mengukur minat pencarian relatif, bukan penjualan, jumlah transaksi, atau pangsa pasar. Perbandingan level antarplatform harus dilakukan dengan hati-hati dan bergantung pada cara data Google Trends dikumpulkan serta dinormalisasi.

## Tujuan

1. Mendeskripsikan perubahan minat pencarian bulanan selama Januari 2020–Desember 2025.
2. Menganalisis tren, pertumbuhan tahunan, pola musiman, perubahan struktural, dan hubungan antarplatform.
3. Membandingkan pola minat pencarian antarprovinsi, termasuk Jawa dan luar Jawa.
4. Menggabungkan hasil analisis waktu dan regional dalam ringkasan terpadu.

## Dataset

File input: `data/raw/Dataset E-Commerce.xlsx`

- **Time Series:** 72 observasi bulanan, Januari 2020–Desember 2025.
- **Regional:** 34 provinsi.
- **Platform:** Shopee, Tokopedia, Lazada, Blibli, dan TikTok Shop.
- Pada validasi terakhir, tidak ditemukan nilai kosong pada kolom platform yang dianalisis.
- TikTok Shop dianalisis mulai September 2021, menghasilkan 52 observasi aktif.

## Metode analisis

### Persiapan dan pembersihan data

- Membaca sheet `Time Series` dan `Regional`.
- Memvalidasi rentang tanggal, nama kolom, nilai numerik, duplikasi, nilai kosong, dan rentang indeks 0–100.
- Memulai seri TikTok Shop pada September 2021.

### A. Analisis tren waktu

- Statistik deskriptif dan grafik garis dengan rata-rata bergerak.
- Rata-rata tahunan, perubahan year-on-year (YoY), dan CAGR.
- Uji tren Mann–Kendall dan Sen's slope.
- Dekomposisi musiman menggunakan STL.
- Deteksi perubahan struktural eksploratif menggunakan PELT.
- Uji Chow dan perbandingan sebelum-sesudah peristiwa.
- Korelasi Spearman pada level dan perubahan bulanan, serta cross-correlation.

### B. Analisis regional

- Statistik deskriptif dan peringkat provinsi.
- Heatmap indeks per provinsi.
- Platform dengan indeks tertinggi per provinsi.
- Koefisien variasi (CV), rentang, IQR, dan boxplot.
- Uji Friedman, Kendall's W, dan post-hoc Wilcoxon dengan koreksi Holm.
- Perbandingan Jawa dan luar Jawa menggunakan Mann–Whitney U serta rank-biserial correlation.
- Korelasi Spearman lintas provinsi.

Provinsi Jawa didefinisikan sebagai Banten, DKI Jakarta, Jawa Barat, Jawa Tengah, DI Yogyakarta, dan Jawa Timur.

### C. Sintesis

Ringkasan terpadu menggabungkan indikator tren, Sen's slope, CAGR, kekuatan musiman, bulan puncak musiman, perubahan struktural, statistik regional, provinsi tertinggi, dan jumlah provinsi yang memiliki tiap platform sebagai indeks tertinggi.

## Ringkasan hasil eksekusi terakhir

Angka berikut merupakan keluaran aktual dari eksekusi lokal yang dilaporkan. Hasil ini bersifat **deskriptif awal**, belum merupakan kesimpulan final sebelum audit metode dan hasil statistik diselesaikan.

### Validasi

| Pemeriksaan | Hasil |
|---|---:|
| Observasi bulanan | 72 |
| Periode | Januari 2020–Desember 2025 |
| Provinsi | 34 |
| Nilai kosong Time Series | 0 |
| Nilai kosong Regional | 0 |
| Observasi aktif TikTok Shop | 52 |
| Awal periode TikTok Shop | September 2021 |

### Statistik deskriptif time series

| Platform | N | Rata-rata | Simpangan baku | Minimum | Maksimum | CV (%) | Bulan puncak |
|---|---:|---:|---:|---:|---:|---:|---|
| Shopee | 72 | 72.333 | 12.345 | 53 | 100 | 17.067 | April 2022 |
| Tokopedia | 72 | 54.319 | 14.589 | 29 | 100 | 26.858 | Mei 2020 |
| Lazada | 72 | 41.306 | 21.946 | 12 | 97 | 53.131 | Mei 2020 |
| Blibli | 72 | 67.500 | 15.304 | 35 | 100 | 22.673 | Maret 2022 |
| TikTok Shop | 52 | 49.038 | 23.363 | 13 | 100 | 47.643 | Juni 2023 |

### Ringkasan tren dan pola waktu

| Platform | Tren Mann–Kendall | p-value | Sen's slope per tahun | CAGR (%) | Kekuatan musiman |
|---|---|---:|---:|---:|---:|
| Shopee | Menurun | < 0.001* | -5.143 | -5.028 | 0.122 |
| Tokopedia | Menurun | < 0.001* | -7.034 | -14.104 | 0.231 |
| Lazada | Menurun | < 0.001* | -10.523 | -25.676 | 0.478 |
| Blibli | Meningkat | < 0.001* | 4.641 | 6.393 | 0.094 |
| TikTok Shop | Tidak ada tren monoton signifikan | 0.262 | -3.647 | 15.856 | 0.182 |

\*Output Python menampilkan `0.000`; p-value tidak benar-benar nol. Untuk pelaporan, gunakan format seperti **p < 0.001** jika nilai presisi dari output mendukungnya.

Berdasarkan output awal, Mann–Kendall mengindikasikan tren menurun pada Shopee, Tokopedia, dan Lazada; tren meningkat pada Blibli; serta tidak ditemukan tren monoton yang signifikan pada TikTok Shop pada taraf 5%. Interpretasi tersebut perlu dikonfirmasi dengan pemeriksaan implementasi dan asumsi uji.

### Ringkasan regional

| Platform | Rata-rata regional | CV regional (%) | Provinsi dengan indeks tertinggi | Jumlah provinsi dengan indeks tertinggi untuk platform |
|---|---:|---:|---|---:|
| Shopee | 56.353 | 38.493 | DI Yogyakarta | 5 |
| Tokopedia | 27.853 | 66.202 | DKI Jakarta | 1 |
| Lazada | 39.794 | 51.402 | Banten | 1 |
| Blibli | 37.647 | 46.717 | DKI Jakarta | 0 |
| TikTok Shop | 70.294 | 25.304 | Jawa Barat | 27 |

Jumlah provinsi pada kolom terakhir berasal dari aturan memilih nilai indeks maksimum per provinsi. Hasil platform dominan harus dibaca hati-hati karena indeks Google Trends dapat dinormalisasi relatif terhadap kueri atau seri yang digunakan.

## Output

Setelah `analysis.py` selesai dijalankan:

- Tabel analisis tersimpan di `output_analisis/hasil_analisis.xlsx`.
- Grafik disimpan dalam folder `output_analisis/`, termasuk grafik tren, dekomposisi STL, heatmap musiman, structural break, korelasi, heatmap regional, boxplot, dan korelasi regional.

Nama file grafik ditentukan oleh fungsi penyimpanan di `analysis.py`.

## Instalasi dan menjalankan proyek

Disarankan menggunakan Python 3.12 pada Windows untuk mengurangi potensi ketidakcocokan dependensi.

1. Buka folder proyek di VS Code.
2. Buat dan aktifkan virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Instal dependensi:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Pastikan file Excel ada di `data/raw/Dataset E-Commerce.xlsx`.
5. Jalankan analisis:

   ```powershell
   python analysis.py
   ```

## Peringatan dan keterbatasan

- `PendingDeprecationWarning` dari Seaborn yang muncul saat pembuatan boxplot bukan error fatal; program tetap selesai dan menulis output. Peringatan dapat ditangani melalui pembaruan kode plotting atau penyesuaian versi dependensi.
- Eksekusi berhasil tidak otomatis membuktikan bahwa seluruh metode statistik telah diimplementasikan secara benar. Validasi lanjutan tetap diperlukan, terutama pada uji Chow, cross-correlation dan penafsiran lag, koreksi pengujian berganda, serta asumsi pengujian.
- CAGR TikTok Shop perlu ditafsirkan hati-hati karena tahun awal 2021 hanya mencakup bulan aktif sejak September.
- Data Google Trends bersifat relatif dan berbasis sampel. Nilainya dapat berubah antarunduhan.
- Pencarian nama platform tidak selalu merepresentasikan niat membeli.
- Korelasi tidak membuktikan hubungan sebab-akibat.
- PELT bersifat eksploratif; tanggal perubahan tidak otomatis menunjukkan dampak kausal suatu peristiwa.

## Status proyek

- [x] Script berjalan sampai tahap ekspor output.
- [x] Validasi struktur dasar dataset berhasil.
- [x] Output Excel dan grafik dihasilkan.
- [ ] Audit akhir seluruh metode statistik dan interpretasi.
- [ ] Pelengkapan visualisasi regional yang belum tersedia, termasuk diagram batang B2 jika diperlukan untuk kesesuaian penuh dengan metodologi.


## Notebook final untuk VS Code

Gunakan `notebooks/Analisis_Google_Trends_Ecommerce_VSCODE_FINAL.ipynb`. Notebook ini mempertahankan struktur analisis sumber (A1–A6, B1–B7, dan C), memperbaiki penentuan lokasi dataset, menambahkan validasi input, menangani kasus khusus pada uji Chow/Wilcoxon, serta menyimpan p-value korelasi dan koreksi Holm. Jalankan semua sel berurutan setelah dependensi diinstal.
