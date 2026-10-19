# Laporan Analisis Regional Google Trends E-Commerce Indonesia (2020–2025)

## 1. Data yang Digunakan

Analisis utama berfokus sepenuhnya pada dimensi **regional** menggunakan data *by region* dari Google Trends yang mencakup 34 provinsi di Indonesia untuk lima platform *e-commerce*: Shopee, Tokopedia, Lazada, Blibli, dan TikTok Shop.

## 2. Validasi Data Regional

| Pemeriksaan | Hasil yang diharapkan | Status |
|---|---:|:---:|
| Jumlah provinsi | 34 | Valid |
| Jumlah platform | 5 | Valid |
| Jumlah indeks regional | 170 | Valid |
| Nilai kosong (*missing values*) | 0 | Terverifikasi Lengkap |
| Periode pengamatan | 2020–2025 | Valid |

> **Catatan Konseptual:** $170 \text{ indeks regional} = 34 \text{ provinsi} \times 5 \text{ platform}$. Setiap provinsi memiliki tepat **satu nilai indeks agregat untuk setiap platform** yang mewakili akumulasi minat penelusuran selama periode 2020–2025. Analisis regional ini **bukan** terdiri dari 72 observasi bulanan per provinsi (observasi 72 bulanan merupakan data deret waktu nasional pada lembar terpisah `Time Series`).

---

## 3. Statistik Deskriptif Regional

Statistik deskriptif dihitung berdasarkan agregasi level spasial provinsi ($N = 34$):

| Platform | N Provinsi | Mean | Median | Std. Dev. | Minimum | Maksimum |
|---|---:|---:|---:|---:|---:|---:|
| **Shopee** | 34 | 56.35 | 55.50 | 21.69 | 21 | 100 |
| **Tokopedia** | 34 | 27.85 | 22.00 | 18.44 | 12 | 100 |
| **Lazada** | 34 | 39.79 | 33.00 | 20.46 | 18 | 100 |
| **Blibli** | 34 | 37.65 | 33.50 | 17.59 | 14 | 100 |
| **TikTok Shop** | 34 | 70.29 | 73.50 | 17.79 | 38 | 100 |

### Temuan Deskriptif:
- **TikTok Shop** mencatat rata-rata minat pencarian tertinggi di seluruh provinsi (Mean = 70.29, Median = 73.50), dengan batas bawah tertinggi (Minimum = 38).
- **Shopee** berada di urutan kedua (Mean = 56.35, Median = 55.50), disusul **Lazada** (Mean = 39.79) dan **Blibli** (Mean = 37.65).
- **Tokopedia** memiliki rata-rata terendah secara nasional (Mean = 27.85, Median = 22.00), namun mencapai nilai puncak 100 di DKI Jakarta.

---

## 4. Heatmap Sebaran Regional

Visualisasi heatmap (`output_analisis/B2_heatmap_provinsi.png`) memperlihatkan intensitas relatif antarplatform di seluruh provinsi:
- Konsentrasi minat tertinggi di Pulau Jawa tampak merata di hampir semua platform (terutama Shopee, TikTok Shop, Tokopedia, dan Blibli).
- Di luar Jawa, TikTok Shop mempertahankan indeks tinggi di hampir semua provinsi luar Jawa, sementara platform lain mengalami penurunan indeks yang cukup signifikan.

---

## 5. Analisis Korelasi Spearman Antarplatform Lintas Provinsi

Uji korelasi peringkat Spearman digunakan untuk mengukur arah dan kekuatan keterkaitan pola sebaran spasial antarplatform lintas 34 provinsi.

### Matriks Korelasi Spearman:
| Platform | Shopee | Tokopedia | Lazada | Blibli | TikTok Shop |
|---|---:|---:|---:|---:|---:|
| **Shopee** | 1.000 | 0.810* | 0.639* | 0.843* | 0.577* |
| **Tokopedia** | 0.810* | 1.000 | 0.597* | 0.813* | 0.298 ($p = 0.088$) |
| **Lazada** | 0.639* | 0.597* | 1.000 | 0.748* | 0.602* |
| **Blibli** | 0.843* | 0.813* | 0.748* | 1.000 | 0.469* |
| **TikTok Shop** | 0.577* | 0.298 | 0.602* | 0.469* | 1.000 |

### Uji Signifikansi Berpasangan dengan Koreksi Multi-Uji Holm:
Penentuan signifikansi statistik wajib merujuk pada *p-value* yang telah disesuaikan dengan koreksi **Holm–Bonferroni** ($p_{\text{Holm}}$):

| Pasangan Platform | Spearman Rho ($r_s$) | Raw $p$-value | $p$-value Holm | Signifikan ($\alpha = 0.05$) |
|---|---:|---:|---:|:---:|
| **Shopee – Blibli** | **0.8433** | < 0.0001 | < 0.0001 | **Ya** |
| **Tokopedia – Blibli** | 0.8132 | < 0.0001 | < 0.0001 | **Ya** |
| **Shopee – Tokopedia** | 0.8102 | < 0.0001 | < 0.0001 | **Ya** |
| **Lazada – Blibli** | 0.7480 | < 0.0001 | < 0.0001 | **Ya** |
| **Shopee – Lazada** | 0.6392 | < 0.0001 | 0.0003 | **Ya** |
| **Lazada – TikTok Shop** | 0.6017 | 0.0002 | 0.0008 | **Ya** |
| **Tokopedia – Lazada** | 0.5969 | 0.0002 | 0.0008 | **Ya** |
| **Shopee – TikTok Shop** | 0.5772 | 0.0004 | 0.0011 | **Ya** |
| **Blibli – TikTok Shop** | 0.4690 | 0.0051 | 0.0103 | **Ya** |
| **Tokopedia – TikTok Shop** | 0.2975 | 0.0875 | 0.0875 | **Tidak** |

> Sebanyak **9 dari 10 pasangan** terbukti berkorelasi positif signifikan ($p_{\text{Holm}} < 0.05$). Satu-satunya hubungan yang **tidak signifikan** secara statistik adalah antara Tokopedia dan TikTok Shop ($p_{\text{Holm}} = 0.0875$).

### Interpretasi Ilmiah untuk Paper:
1. **Interpretasi Korelasi Shopee – Blibli ($r_s = 0.8433$):**  
   Korelasi Spearman yang sangat kuat dan signifikan ($r_s = 0.8433, p_{\text{Holm}} < 0.0001$) mengindikasikan adanya **keselarasan pola peringkat regional yang kuat dan searah (*strong co-directional regional ranking pattern*)**. Artinya, provinsi yang menempatkan minat pencarian Shopee pada peringkat relatif tinggi secara konsisten juga menempatkan Blibli pada peringkat relatif tinggi dalam sebaran geografis masing-masing platform.  
   **Peringatan Akademik:** Nilai korelasi ini **BUKAN bukti bahwa kedua platform memiliki basis pengguna aktif, volume transaksi, atau angka penjualan yang mirip**. Korelasi Spearman hanya mengukur keserupaan peringkat spasial, bukan volume absolut transaksi.
2. **Klaster Platform Tradisional:** Korelasi erat antara Shopee, Tokopedia, dan Blibli ($r_s > 0.80$) mempertegas bahwa ketiga platform mapan ini memiliki jejak geografis penelusuran digital yang identik di wilayah perkotaan/Jawa.
3. **Divergensi TikTok Shop:** Tidak signifikannya korelasi antara Tokopedia dan TikTok Shop ($r_s = 0.2975, p_{\text{Holm}} = 0.0875$) membuktikan bahwa TikTok Shop berhasil menembus pasar luar Jawa dan wilayah timur secara mandiri tanpa tergantung pada sentra pengguna Tokopedia.

---

## 6. Uji Beda Mann–Whitney U: Jawa vs Luar Jawa

Pengujian dilakukan untuk membandingkan sebaran minat antara provinsi di Pulau Jawa (N = 6: Banten, DKI Jakarta, Jawa Barat, Jawa Tengah, DI Yogyakarta, Jawa Timur) dengan luar Jawa (N = 28):

| Platform | N Jawa | N Luar Jawa | Median Jawa | Median Luar Jawa | Nilai U | p-value | p Holm | Signifikan (α=5%) |
|---|---:|---:|---:|---:|---:|---:|---:|:---:|
| **Shopee** | 6 | 28 | 89.50 | 54.00 | 168.0 | 0.00016 | 0.00079 | **Ya** |
| **Tokopedia** | 6 | 28 | 53.50 | 20.50 | 167.0 | 0.00019 | 0.00079 | **Ya** |
| **Lazada** | 6 | 28 | 78.50 | 32.00 | 168.0 | 0.00016 | 0.00079 | **Ya** |
| **Blibli** | 6 | 28 | 63.50 | 31.50 | 162.5 | 0.00042 | 0.00084 | **Ya** |
| **TikTok Shop** | 6 | 28 | 93.00 | 69.50 | 150.0 | 0.00307 | 0.00307 | **Ya** |

### Temuan Uji Beda:
- Kelima platform menunjukkan perbedaan minat pencarian yang **signifikan secara statistik** (p Holm < 0.05) antara Jawa dan luar Jawa, di mana nilai median di Pulau Jawa selalu lebih tinggi.
- Kesenjangan tertinggi terjadi pada Tokopedia dan Lazada (penurunan median lebih dari 50% di luar Jawa), sedangkan TikTok Shop mencatat perbedaan terkecil dengan median luar Jawa tetap tinggi di angka 69.50.

---

## 7. Ringkasan Dominasi Regional & Evaluasi Seri (Tie)

Dalam penulisan paper, metode yang diacu adalah **Dominasi Bersama (*Joint Dominance*)**:

| Platform | Dominasi Bersama (*Joint Dominance*) [Standar Paper] | Dominasi Terbagi (*Shared*) | Dominasi Bawaan (*idxmax*) [Artefak Bias] | Provinsi Puncak | Indeks Puncak |
|---|---:|---:|---:|---|---:|
| **TikTok Shop** | **27** | 27.0 | 27 | Jawa Barat | 100 |
| **Shopee** | **5** | 4.5 | 5 | DI Yogyakarta | 100 |
| **Blibli** | **2 (DKI Jakarta & Bali)** | 1.0 | **0** | **DKI Jakarta** | **100** |
| **Tokopedia** | **1** | 0.5 | 1 | DKI Jakarta | 100 |
| **Lazada** | **1** | 1.0 | 1 | Banten | 100 |
| **Total** | **36\*** | 34.0 | 34 | - | - |

*\*Total joint dominance berjumlah 36 (> 34) karena terdapat 2 provinsi dengan nilai kembar tertinggi (tie).*

### Penjelasan Kasus Blibli (Mengapa Sebelumnya Tercatat 0?):
1. **DKI Jakarta (Nilai Puncak 100):**  
   Tokopedia dan Blibli sama-sama mencatat indeks tertinggi **100**. Keduanya berhak dinyatakan sebagai pemegang minat tertinggi di DKI Jakarta.
2. **Bali (Nilai Puncak 54):**  
   Shopee dan Blibli sama-sama mencatat indeks tertinggi **54**. Keduanya berhak dinyatakan sebagai pemegang minat tertinggi di Bali.
3. **Penyebab Teknis Angka 0:**  
   Fungsi bawaan `pandas.idxmax()` hanya mengambil kolom pertama yang ditemui ketika ada skor seri. Urutan kolom dataframe mentah menempatkan Shopee dan Tokopedia mendahului Blibli, sehingga Blibli tereliminasi secara artifisial.
4. **Kaidah Pelaporan Paper:**  
   Gunakan metode **Dominasi Bersama (*Joint Dominance*)** dan laporkan secara transparan bahwa **Blibli unggul/seri di 2 provinsi (DKI Jakarta dan Bali)**, bukan 0.

---

## 8. Catatan Metodologi Kritis: Skala Relatif Google Trends

> [!WARNING]
> **Peringatan Metodologi & Batasan Interpretasi Ilmiah:**
> 1. **Dilarang Menyamakan Indeks Penelusuran dengan Penjualan / Transaksi Riil:** Indeks Google Trends merepresentasikan minat penelusuran digital (*digital consumer search interest*), bukan volume transaksi keuangan (*GMV*), jumlah pesanan, atau pangsa pasar (*market share*).
> 2. **Normalisasi Independen Tiap Platform:** Data masing-masing platform diekspor dari Google Trends dalam berkas terpisah, sehingga skala 0–100 dinormalisasi secara independen terhadap titik puncak internal platform tersebut.
> 3. **Arti Indeks Puncak 100:** Skor 100 pada Blibli di DKI Jakarta menunjukkan bahwa DKI Jakarta adalah provinsi dengan minat pencarian relatif tertinggi *bagi Blibli*, bukan berarti volume pencarian absolut Blibli menyamai atau mengungguli Tokopedia atau TikTok Shop.
> 4. **Makna Statistik Deskriptif Spasial:** Nilai rata-rata regional (misal: TikTok Shop 70.29 vs Tokopedia 27.85) menggambarkan tingkat pemerataan distribusi spasial (apakah tersebar merata secara nasional atau terpusat di kawasan metropolitan), bukan ukuran popularitas absolut.