# LAPORAN VALIDASI DATA DAN METODOLOGI PENELITIAN

**Judul Penelitian:**  
*Digital Consumer Interest in Indonesian E-Commerce: A Google Trends Analysis of Regional Search Patterns, 2020–2025*

**Peran:** Research Assistant & Data Analyst  
**Tanggal Evaluasi:** 19 Oktober 2026  
**Status Audit Keseluruhan:** **TERVERIFIKASI LENGKAP & DAPAT DIREPRODUKSI (100% REPRODUCIBLE)**

---

## 1. Inventarisasi dan Pemeriksaan Berkas Workspace

Berdasarkan penelusuran struktur direktori proyek `d:\Interest in Indonesian E-Commerce`, berkas penelitian teridentifikasi sebagai berikut:

| Kategori | Lokasi Berkas | Keterangan & Status |
|---|---|---|
| **Dataset Sumber** | `data/raw/Dataset E-Commerce.xlsx` | Berisi dua sheet: `Time Series` (72 observasi nasional) dan `Regional` (34 provinsi). Sheet `Regional` menjadi sumber data tunggal untuk analisis spasial. |
| **Skrip Pemrosesan** | `src/config.py`, `src/data_prep.py` | Modul konfigurasi jalur berkas, daftar platform, dan fungsi standardisasi data. |
| **Skrip Eksekusi Regional** | `run_regional.py` | Skrip eksekusi analisis regional mandiri: validasi, deskriptif, korelasi Spearman, Mann–Whitney U, Holm, dan ekspor. |
| **Dokumentasi Internal** | `doc.md` | Catatan interpretasi ilmiah hasil analisis regional dan penjelasan tie-breaking. |
| **Dokumen Tahapan** | `docs/Tahapan_Analisis_Data.docx` | Dokumen panduan metodologi komprehensif. |
| **Output Tabular** | `output_analisis/hasil_analisis_regional.xlsx` | Lembar kerja berisi seluruh tabel output regional terverifikasi. |
| **Output Visualisasi** | `output_analisis/B2_heatmap_provinsi.png`<br>`output_analisis/B2_ranking_provinsi.png`<br>`output_analisis/B4_boxplot.png`<br>`output_analisis/B6_jawa_vs_luar.png`<br>`output_analisis/B7_korelasi_regional.png` | Seluruh visualisasi grafik beresolusi tinggi tersedia dan sesuai dengan dataset. |
| **Visualisasi Flowchart Baru** | `research_workflow.png` | Diagram alur penelitian standar publikasi ilmiah (resolusi 300 DPI) telah dibuat. |
| **Draf Metodologi Baru** | `research_method_final.md` | Draf bab II Research Method dalam bahasa Inggris akademik siap disitasi ke paper. |

---

## 2. Hasil Audit Kualitas Data Spasial

Pemeriksaan konsistensi dan integritas data pada sheet `Regional` menunjukkan kepatuhan penuh terhadap standar data penelitian:

| Parameter Uji | Syarat Metodologis | Hasil Aktual | Status |
|---|---|---|:---:|
| **Jumlah Provinsi ($N$)** | Tepat 34 provinsi (BPS) | 34 entitas administratif | **Valid** |
| **Jumlah Platform** | 5 platform utama | Shopee, Tokopedia, Lazada, Blibli, TikTok Shop | **Valid** |
| **Total Observasi** | $34 \times 5 = 170$ observasi | 170 sel terisi | **Valid** |
| **Nilai Kosong (*Missing Values*)** | 0 sel | 0 sel (`NaN = 0`) | **Valid** |
| **Duplikasi Wilayah** | 0 duplikasi nama provinsi | 0 duplikasi | **Valid** |
| **Rentang Nilai Indeks** | Berada dalam batas $[0, 100]$ | $\min = 12$, $\max = 100$ | **Valid** |
| **Periode Observasi** | Agregat 2020–2025 | 2020–2025 (akumulasi relatif) | **Valid** |

### Stratifikasi Geografis:
- **Provinsi Pulau Jawa ($n_1 = 6$):** Banten, DKI Jakarta, Jawa Barat, Jawa Tengah, DI Yogyakarta, Jawa Timur.
- **Provinsi Luar Pulau Jawa ($n_2 = 28$):** Aceh, Bali, Bengkulu, Gorontalo, Jambi, Kalimantan Barat, Kalimantan Selatan, Kalimantan Tengah, Kalimantan Timur, Kalimantan Utara, Kepulauan Bangka Belitung, Kepulauan Riau, Lampung, Maluku, Maluku Utara, Nusa Tenggara Barat, Nusa Tenggara Timur, Papua, Papua Barat, Riau, Sulawesi Barat, Sulawesi Selatan, Sulawesi Tengah, Sulawesi Tenggara, Sulawesi Utara, Sumatera Barat, Sumatera Selatan, Sumatera Utara.

---

## 3. Verifikasi Perhitungan Statistik Deskriptif

Setiap metrik deskriptif telah dihitung ulang secara mandiri langsung dari data mentah dan cocok 100% dengan hasil di `doc.md` dan `run_regional.py`:

| Platform | N Provinsi | Mean ($\bar{x}$) | Median ($\tilde{x}$) | Std. Dev. ($s$) | Minimum | Maksimum | Provinsi Puncak ($\max = 100$) |
|---|---:|---:|---:|---:|---:|---:|---|
| **Shopee** | 34 | 56.35 | 55.50 | 21.69 | 21 (Papua) | 100 | DI Yogyakarta |
| **Tokopedia** | 34 | 27.85 | 22.00 | 18.44 | 12 (Maluku) | 100 | DKI Jakarta |
| **Lazada** | 34 | 39.79 | 33.00 | 20.46 | 18 (NTB) | 100 | Banten |
| **Blibli** | 34 | 37.65 | 33.50 | 17.59 | 14 (Maluku) | 100 | DKI Jakarta |
| **TikTok Shop** | 34 | 70.29 | 73.50 | 17.79 | 38 (Maluku, NTT) | 100 | Jawa Barat |

---

## 4. Verifikasi Korelasi Spearman & Koreksi Multi-Uji Holm

Uji korelasi peringkat Spearman ($r_s$) dilakukan pada 10 kombinasi pasangan platform lintas 34 provinsi. Nilai $p$ disesuaikan menggunakan koreksi sekuensial Holm–Bonferroni untuk mengendalikan *Family-Wise Error Rate* ($\alpha = 0.05$):

### Matriks Korelasi Spearman Antarplatform:
| Platform | Shopee | Tokopedia | Lazada | Blibli | TikTok Shop |
|---|---:|---:|---:|---:|---:|
| **Shopee** | 1.0000 | 0.8102 | 0.6392 | 0.8433 | 0.5772 |
| **Tokopedia** | 0.8102 | 1.0000 | 0.5969 | 0.8132 | 0.2975 |
| **Lazada** | 0.6392 | 0.5969 | 1.0000 | 0.7480 | 0.6017 |
| **Blibli** | 0.8433 | 0.8132 | 0.7480 | 1.0000 | 0.4690 |
| **TikTok Shop** | 0.5772 | 0.2975 | 0.6017 | 0.4690 | 1.0000 |

### Hasil Uji Hipotesis Berpasangan (10 Pasangan):
| No | Pasangan Platform | Spearman Rho ($r_s$) | Raw $p$-value | $p$-value Holm | Signifikan ($\alpha = 0.05$) | Interpretasi Spasial |
|:---:|---|---:|---:|---:|:---:|---|
| 1 | **Shopee – Blibli** | **0.8433** | $4.27 \times 10^{-10}$ | $4.27 \times 10^{-9}$ | **Ya** | Keselarasan pola peringkat spasial sangat kuat |
| 2 | **Tokopedia – Blibli** | **0.8132 Manual / Calc** | $4.76 \times 10^{-9}$ | $4.28 \times 10^{-8}$ | **Ya** | Jejak geografis metropolitan identik |
| 3 | **Shopee – Tokopedia** | **0.8102** | $5.90 \times 10^{-9}$ | $4.72 \times 10^{-8}$ | **Ya** | Jejak geografis metropolitan identik |
| 4 | **Lazada – Blibli** | **0.7480** | $1.76 \times 10^{-7}$ | $1.23 \times 10^{-6}$ | **Ya** | Keselarasan pola peringkat tinggi |
| 5 | **Shopee – Lazada** | **0.6392** | $4.87 \times 10^{-5}$ | $0.00029$ | **Ya** | Korelasi spasial moderat ke kuat |
| 6 | **Lazada – TikTok Shop** | **0.6017** | $0.00015$ | $0.00076$ | **Ya** | Korelasi sebaran moderat |
| 7 | **Tokopedia – Lazada** | **0.5969** | $0.00018$ | $0.00076$ | **Ya** | Korelasi sebaran moderat |
| 8 | **Shopee – TikTok Shop** | **0.5772** | $0.00037$ | $0.00110$ | **Ya** | Korelasi sebaran moderat |
| 9 | **Blibli – TikTok Shop** | **0.4690** | $0.00511$ | $0.01023$ | **Ya** | Korelasi sebaran sedang |
| 10 | **Tokopedia – TikTok Shop** | **0.2975** | **0.08745** | **0.08745** | **Tidak** | **Divergensi spasial: TikTok Shop tidak berkorelasi signifikan dengan Tokopedia** |

---

## 5. Verifikasi Uji Mann–Whitney U: Pulau Jawa vs Luar Jawa

Uji Mann–Whitney $U$ dua sisi membandingkan distribusi indeks minat penelusuran antara 6 provinsi di Pulau Jawa dan 28 provinsi di luar Jawa:

| Platform | $N_{\text{Jawa}}$ | $N_{\text{Luar}}$ | Median Jawa | Median Luar Jawa | Nilai $U$ | Raw $p$-value | $p$-value Holm | Rank-Biserial $r_{rb}$ | Signifikan ($\alpha = 0.05$) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|:---:|
| **Shopee** | 6 | 28 | 89.50 | 54.00 | 168.0 | 0.00016 | 0.00079 | 1.0000 | **Ya** |
| **Tokopedia** | 6 | 28 | 53.50 | 20.50 | 167.0 | 0.00019 | 0.00079 | 0.9881 | **Ya** |
| **Lazada** | 6 | 28 | 78.50 | 32.00 | 168.0 | 0.00016 | 0.00079 | 1.0000 | **Ya** |
| **Blibli** | 6 | 28 | 63.50 | 31.50 | 162.5 | 0.00042 | 0.00084 | 0.9345 | **Ya** |
| **TikTok Shop** | 6 | 28 | 93.00 | 69.50 | 150.0 | 0.00307 | 0.00307 | 0.7857 | **Ya** |

### Evaluasi Statistik:
1. Seluruh kelima platform menunjukkan perbedaan minat pencarian yang **signifikan secara statistik** ($p_{\text{Holm}} < 0.05$) antara Pulau Jawa dan luar Jawa.
2. Nilai Rank-Biserial correlation ($r_{rb}$) pada Shopee dan Lazada mencapai nilai maksimum $1.0000$, menandakan bahwa seluruh provinsi di Pulau Jawa memiliki peringkat indeks yang lebih tinggi daripada mayoritas provinsi luar Jawa tanpa tumpang tindih signifikan.
3. TikTok Shop memiliki efek disparitas terendah ($r_{rb} = 0.7857$), dengan median luar Jawa tetap tinggi sebesar 69.50, membuktikan penetrasi geografis TikTok Shop yang lebih merata ke wilayah non-metropolitan dibandingkan platform konvensional.

---

## 6. Masalah Metodologis Kritis: Penanganan Seri (Tie-Breaking) Dominasi Regional

Ditemukan permasalahan algoritmik penting yang berpotensi membiaskan temuan jika tidak dilaporkan dengan teliti:

### Masalah Algoritmik:
- Fungsi `pandas.idxmax()` secara baku hanya mengembalikan kolom pertama yang ditemui ketika terdapat nilai maksimum kembar (*tie*).
- Pada urutan kolom tabel asli: `Shopee`, `Tokopedia`, `Lazada`, `Blibli`, `TikTok Shop`.
- Di **DKI Jakarta**, Tokopedia dan Blibli **sama-sama bernilai 100**. Karena Tokopedia berada di kolom sebelum Blibli, Blibli diabaikan.
- Di **Bali**, Shopee dan Blibli **sama-sama bernilai 54**. Karena Shopee berada di kolom sebelum Blibli, Blibli kembali diabaikan.
- Dampaknya: Jika memakai `idxmax()`, Blibli tercatat memiliki 0 provinsi dominan, yang merupakan distorsi artifisial akibat urutan kolom.

### Solusi Metodologi Baku Paper (Joint Dominance):
Gunakan pendekatan **Dominasi Bersama (*Joint Dominance*)**, di mana setiap platform yang berbagi nilai puncak di suatu provinsi sama-sama diakui:

| Platform | Dominasi Bersama (*Joint Dominance*) | Dominasi Bawaan (`idxmax` Bias) | Provinsi Skor Puncak | Skor Puncak |
|---|---:|---:|---|---:|
| **TikTok Shop** | **27 provinsi** | 27 | Jawa Barat | 100 |
| **Shopee** | **5 provinsi** | 5 | DI Yogyakarta | 100 |
| **Blibli** | **2 provinsi (DKI Jakarta & Bali)** | **0 (Tersingkir akibat bias urutan)** | DKI Jakarta | 100 |
| **Tokopedia** | **1 provinsi (DKI Jakarta)** | 1 | DKI Jakarta | 100 |
| **Lazada** | **1 provinsi (Banten)** | 1 | Banten | 100 |
| **Total** | **36\*** | 34 | - | - |

*\*Total berjumlah 36 (> 34) karena terdapat 2 provinsi dengan nilai kembar tertinggi.*

---

## 7. Batasan Metodologi yang Wajib Diperhatikan Penulis Paper

1. **Skala Relatif Bounded (0–100):**  
   Indeks Google Trends mengukur proporsi minat pencarian relatif suatu topik terhadap total penelusuran di wilayah tersebut, bukan volume penelusuran absolut, transaksi e-commerce, atau GMV.
2. **Normalisasi Independen:**  
   Dataset untuk setiap platform diekspor secara terpisah dari Google Trends. Oleh karena itu, masing-masing kolom memiliki titik puncak 100 sendiri. **Dilarang membandingkan angka rata-rata antarplatform (misal: TikTok Shop 70.29 vs Tokopedia 27.85) sebagai ukuran pangsa pasar (*market share*) atau popularitas absolut.**
3. **Bukan Data Bulanan:**  
   Dataset regional ini terdiri dari tepat **satu indeks agregat per platform per provinsi** (170 observasi), bukan 72 observasi bulanan per provinsi. Data 72 observasi bulanan adalah data *Time Series* nasional pada sheet terpisah.
4. **Korelasi Spearman Bukan Bukti Kausalitas:**  
   Korelasi Spearman $r_s = 0.8433$ antara Shopee dan Blibli hanya membuktikan bahwa kedua platform memiliki **keselarasan pola peringkat spasial (*co-directional regional ranking pattern*)**, bukan membuktikan kesamaan basis pembeli atau persaingan langsung antar-aplikasi.
5. **Kepatuhan Batasan Analisis:**  
   Penelitian ini **tidak menggunakan** K-Means clustering, PCA, ataupun regresi linier multivariat. Penambahan metode-metode tersebut di luar koridor penelitian yang telah diverifikasi adalah bentuk halusinasi metodologi.

---

## 8. Ringkasan File Baru yang Dibuat

1. [research_method_final.md](file:///d:/Interest%20in%20Indonesian%20E-Commerce/research_method_final.md) — Draf lengkap bagian II. Research Method dalam bahasa Inggris akademik standar publikasi internasional.
2. [research_workflow.png](file:///d:/Interest%20in%20Indonesian%20E-Commerce/research_workflow.png) — Gambar flowchart metodologi beresolusi tinggi (300 DPI) yang mencakup 7 tahapan penelitian sistematis.
3. [validation_report.md](file:///d:/Interest%20in%20Indonesian%20E-Commerce/validation_report.md) — Laporan audit dan validasi data komprehensif ini.
