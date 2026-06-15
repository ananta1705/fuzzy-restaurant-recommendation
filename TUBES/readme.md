# Klasifikasi Sampah Citra Organik & Anorganik
Sistem sederhana untuk mengklasifikasikan sampah **Organik** dan **Anorganik** dari citra digital menggunakan **Decision Tree Custom** (dari nol, tanpa library Machine Learning).

---

## 1. Alur Kerja Kode Program (`test_image_scratch.py`)
1. **Ekstraksi Fitur (Rerata RGB):**
   Setiap gambar di-resize ke $64 \times 64$ piksel. Nilai rata-rata warna *Red* (R), *Green* (G), dan *Blue* (B) dihitung untuk mewakili karakteristik gambar tersebut.
2. **Train-Test Split (80:20):**
   Dataset diacak secara konsisten menggunakan `seed=344`. Sebanyak **16 gambar** digunakan untuk data latih (*Train Set*), dan **4 gambar** digunakan untuk data uji (*Test Set*).
3. **Training Model:**
   Pohon keputusan dibangun rekursif hingga kedalaman maksimum (`max_depth=5`) dengan membagi data berdasarkan nilai **Gini Impurity** terkecil.
4. **Evaluasi & Uji Interaktif:**
   Model diuji terhadap data uji dan menyediakan menu interaktif untuk menguji gambar pilihan pengguna secara GUI.

---

## 2. Struktur Dataset (Total: 20 Gambar)
* **Organik (9 Gambar):** Daun kering, cangkang telur, ampas teh, ampas kopi, apel, jeruk, sisa pisang, kulit sayur, dan sisa makanan dapur.
* **Anorganik (11 Gambar):** Botol plastik, botol kaca, kaleng, kantong kresek, toples kaca, wadah styrofoam, kardus, wadah aluminium, gelas kertas, sendok garpu plastik, dan majalah kertas.

---

## 3. Mengapa Evaluasi Model Bernilai 100%?
1. **Jumlah Data Uji Kecil:** Data uji hanya berisi **4 gambar**. Model berhasil memprediksi ke-4 gambar uji tersebut dengan benar (4 dari 4 benar).
2. **Karakteristik Warna Sangat Jelas (Kontras):** 
   * Sampah **Organik** didominasi warna gelap/alami (hijau, cokelat).
   * Sampah **Anorganik** didominasi warna terang/sintetis (putih, abu-abu mengkilap, biru).
   Karena tidak ada pencampuran warna yang rumit antar-kategori di dataset ini, model dapat dengan mudah memisahkannya secara matematis.
3. **Gambar Bersih:** Latar belakang gambar polos/bersih, sehingga rata-rata warna RGB murni mewakili objek sampahnya sendiri tanpa *noise*.

> [!NOTE]
> **Catatan Akademis:** Hasil 100% ini terjadi karena kesederhanaan variasi dataset skala kecil. Jika jumlah gambar ditambah menjadi ratusan dengan latar belakang yang ramai (dunia nyata), akurasi model akan turun karena warna RGB rata-ratanya akan saling tumpang tindih (*overlap*).
