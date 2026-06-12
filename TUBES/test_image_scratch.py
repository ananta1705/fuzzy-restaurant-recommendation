# ==============================================================================
# KLASIFIKASI GAMBAR SAMPAH ORGANIK DAN ANORGANIK DENGAN DECISION TREE CUSTOM (NO-ML-LIB)
# Untuk Mendukung Pengelolaan Lingkungan Hidup Berkelanjutan
# ==============================================================================

import os       # Library bawaan Python untuk operasi sistem file (buat folder, baca path, dll.)
import cv2      # Library OpenCV untuk membaca, mengubah ukuran, dan menampilkan gambar
import numpy as np  # Library NumPy untuk komputasi numerik, dipakai untuk hitung rata-rata piksel
import random   # Library bawaan Python untuk menghasilkan angka acak (shuffle dataset, dummy image)
import sys      # Library bawaan Python untuk interaksi sistem (exit program, cek platform OS)

# Cek apakah sistem operasi yang digunakan adalah Windows
if sys.platform.startswith('win'):
    import os                   # Import ulang os (untuk kejelasan dalam blok ini)
    os.system('color')          # Jalankan perintah 'color' agar terminal Windows mendukung kode warna ANSI

# Definisi kode warna ANSI untuk mewarnai teks di terminal
GREEN   = "\033[1;32m"   # Warna hijau tebal — digunakan untuk label Organik & sukses
BLUE    = "\033[1;34m"   # Warna biru tebal  — digunakan untuk label Anorganik
YELLOW  = "\033[1;33m"   # Warna kuning tebal — digunakan untuk judul & instruksi
RED     = "\033[1;31m"   # Warna merah tebal  — digunakan untuk peringatan & error
CYAN    = "\033[1;36m"   # Warna cyan tebal   — digunakan untuk info proses & tabel
MAGENTA = "\033[1;35m"   # Warna magenta tebal — digunakan untuk border & header utama
RESET   = "\033[0m"      # Reset warna ke default terminal
BOLD    = "\033[1m"      # Cetak teks dengan tebal (bold)
UNDERLINE = "\033[4m"    # Cetak teks dengan garis bawah (underline)


# ==============================================================================
# FUNGSI: TAMPILKAN SLIDE EDUKASI CARA KERJA DECISION TREE
# Fungsi ini menampilkan 5 slide penjelasan teori & matematika Decision Tree
# secara interaktif di terminal, slide per slide
# ==============================================================================
def tampilkan_cara_kerja():
    """Menampilkan presentasi slide-by-slide mengenai cara kerja dan matematika Decision Tree"""

    # Daftar isi semua slide dalam bentuk list string (f-string berwarna)
    slides = [
        # Slide 1: Pengantar — menjelaskan apa itu Decision Tree dan struktur dasarnya
        f"""
{MAGENTA}================================================================================{RESET}
{BOLD}{YELLOW}               SLIDE 1: PENGANTAR ALGORITMA DECISION TREE (POHON KEPUTUSAN)      {RESET}
{MAGENTA}================================================================================{RESET}
  * Decision Tree adalah model prediktif terawasi (supervised) yang bekerja secara
    rekursif membagi dataset berdasarkan pertanyaan-pertanyaan logika biner (Ya/Tidak).
  * Struktur dasar pohon terdiri dari:
    1. {BOLD}{CYAN}Root Node (Node Akar){RESET}   : Titik awal pembagian seluruh dataset.
    2. {BOLD}{CYAN}Branch Node (Node Cabang){RESET} : Kondisi pengujian fitur (misal: Warna <= threshold).
    3. {BOLD}{CYAN}Leaf Node (Node Daun){RESET}     : Keputusan akhir kelas (Organik atau Anorganik).
  * {BOLD}Mengapa custom scratch?{RESET} Membuktikan bahwa klasifikasi dapat berjalan 
    tanpa bergantung pada framework ML modern (seperti scikit-learn).
{MAGENTA}================================================================================{RESET}
{YELLOW}Tekan ENTER untuk lanjut ke slide berikutnya...{RESET}""",

        # Slide 2: Ekstraksi Fitur — menjelaskan proses membaca gambar dan mengambil nilai RGB
        f"""
{MAGENTA}================================================================================{RESET}
{BOLD}{YELLOW}               SLIDE 2: PROSES EKSTRAKSI FITUR CITRA (WARNA RGB)                {RESET}
{MAGENTA}================================================================================{RESET}
  * Gambar dari dataset asli dibaca menggunakan library {BOLD}OpenCV{RESET}.
  * Citra diubah ukurannya menjadi {BOLD}64x64 piksel{RESET} untuk menyamakan dimensi.
  * Fitur numerik yang digunakan adalah {BOLD}Rerata Intensitas Warna (Mean RGB){RESET}:
    1. {BOLD}{RED}Rerata Warna Merah (Red Mean){RESET}   - Intensitas rata-rata channel Red.
    2. {BOLD}{GREEN}Rerata Warna Hijau (Green Mean){RESET} - Intensitas rata-rata channel Green.
    3. {BOLD}{BLUE}Rerata Warna Biru (Blue Mean){RESET}   - Intensitas rata-rata channel Blue.
  * Nilai rata-rata berkisar antara {BOLD}0.0 hingga 255.0{RESET}.
  * Karakteristik umum:
    - Sampah Organik (daun, pisang) cenderung dominan Hijau/Cokelat.
    - Sampah Anorganik (kaleng, botol) cenderung dominan Abu/Biru/Merah terang.
{MAGENTA}================================================================================{RESET}
{YELLOW}Tekan ENTER untuk lanjut ke slide berikutnya...{RESET}""",

        # Slide 3: Gini Impurity — menjelaskan rumus matematika untuk mengukur kemurnian node
        f"""
{MAGENTA}================================================================================{RESET}
{BOLD}{YELLOW}               SLIDE 3: KONSEP MATEMATIKA - GINI IMPURITY (KETIDAKMURNIAN GINI) {RESET}
{MAGENTA}================================================================================{RESET}
  * Gini Impurity mengukur tingkat 'kotor/campuran' sampel dalam suatu node.
  * Rumus Matematika:
      {BOLD}{CYAN}Gini(D) = 1 - sum( p_i^2 ){RESET}
      di mana:
      - {BOLD}D{RESET} adalah kumpulan data sampel di node tersebut.
      - {BOLD}p_i{RESET} adalah probabilitas memilih kelas i secara acak.
  * Nilai Gini Impurity berkisar antara:
    - {BOLD}0.0{RESET} : Node murni (Pure). Semua sampel dalam satu kelas (misal semua Organik).
    - {BOLD}0.5{RESET} : Node paling tidak murni (untuk klasifikasi biner, e.g. 50% Organik, 50% Anorganik).
{MAGENTA}================================================================================{RESET}
{YELLOW}Tekan ENTER untuk lanjut ke slide berikutnya...{RESET}""",

        # Slide 4: Proses Split Terbaik — menjelaskan cara memilih fitur & threshold pemisah terbaik
        f"""
{MAGENTA}================================================================================{RESET}
{BOLD}{YELLOW}               SLIDE 4: PROSES PENCARIAN PEMBAGIAN (SPLIT) TERBAIK              {RESET}
{MAGENTA}================================================================================{RESET}
  * Untuk setiap fitur (Rerata R, G, B), model mengurutkan nilai uniknya dan mencoba
    setiap calon threshold (titik tengah nilai berurutan).
  * Data dibagi menjadi dua cabang: Kiri (<= Threshold) dan Kanan (> Threshold).
  * Kualitas pembagian diukur dengan {BOLD}Weighted Gini Impurity (Rata-rata Terbobot){RESET}:
      {BOLD}{CYAN}Gini_split = (|D_kiri| / |D|) * Gini(D_kiri) + (|D_kanan| / |D|) * Gini(D_kanan){RESET}
  * {BOLD}Model memilih fitur & threshold yang menghasilkan Gini_split paling KECIL.{RESET}
  * Proses ini diulang secara rekursif hingga mencapai kedalaman maksimum (max_depth)
    atau sampel homogen.
{MAGENTA}================================================================================{RESET}
{YELLOW}Tekan ENTER untuk lanjut ke slide berikutnya...{RESET}""",

        # Slide 5: Alur Klasifikasi — menjelaskan proses prediksi gambar secara real-time
        f"""
{MAGENTA}================================================================================{RESET}
{BOLD}{YELLOW}               SLIDE 5: ALUR RUN-TIME KLASIFIKASI CITRA SAMPAH                 {RESET}
{MAGENTA}================================================================================{RESET}
  * Saat Anda memilih file gambar sampah untuk diuji:
    1. Sistem membaca gambar dan menghitung rerata nilai warna RGB.
    2. Nilai Rerata RGB dimasukkan ke pohon keputusan terlatih.
    3. Sistem menyusuri percabangan pohon:
       Jika kondisi logika terpenuhi (<= threshold) -> Belok Kiri.
       Jika tidak (> threshold) -> Belok Kanan.
    4. Setiap langkah penyusuran (Decision Path) dicetak langsung di layar terminal.
    5. Setelah mencapai daun, kelas akhir (Organik/Anorganik) & rekomendasi daur ulang ditampilkan.
{MAGENTA}================================================================================{RESET}
{YELLOW}Tekan ENTER untuk kembali ke menu utama...{RESET}"""
    ]

    # Iterasi setiap slide dan tampilkan satu per satu
    for slide in slides:
        os.system('cls' if os.name == 'nt' else 'clear')  # Bersihkan layar terminal sebelum tiap slide
        print(slide)    # Cetak isi slide ke terminal
        input()         # Tunggu user menekan ENTER sebelum melanjutkan ke slide berikutnya


# ==============================================================================
# BAGIAN 1: GENERATOR GAMBAR DUMMY (SYNTHETIC IMAGE GENERATION)
# Fungsi ini membuat gambar PNG palsu jika folder dataset masih kosong/kurang,
# agar program tetap bisa berjalan meski belum ada dataset asli
# ==============================================================================
def generate_dummy_images(dir_organik, dir_anorganik, num_images=15):
    """
    Membuat file gambar dummy (.png) jika folder dataset memiliki jumlah gambar kurang dari num_images.
    - Sampah Organik: Gambar berwarna dominan Hijau / Cokelat
    - Sampah Anorganik: Gambar berwarna dominan Biru / Merah / Abu-abu
    """
    random.seed(42)     # Atur seed acak agar gambar dummy yang dihasilkan selalu konsisten/reproducible

    # -----------------------------------------------------------------------
    # Generate gambar dummy untuk folder Organik
    # -----------------------------------------------------------------------
    # Ambil daftar file gambar yang sudah ada di folder Organik
    existing_organik = [f for f in os.listdir(dir_organik) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    # Jika jumlah gambar yang ada masih kurang dari target, tambahkan gambar dummy
    if len(existing_organik) < num_images:
        needed = num_images - len(existing_organik)     # Hitung berapa gambar yang masih dibutuhkan
        print(f"Folder Organik memiliki {len(existing_organik)} gambar. Menambahkan {needed} gambar dummy organik...")

        for i in range(needed):
            img = np.zeros((64, 64, 3), dtype=np.uint8)     # Buat kanvas gambar 64x64 piksel, 3 channel (BGR), nilai awal 0 (hitam)

            # Tentukan warna dasar dominan hijau-cokelat (karakteristik sampah organik)
            base_g = random.randint(120, 220)   # Nilai channel Hijau (Green) — dominan tinggi untuk kesan organik
            base_r = random.randint(60, 140)    # Nilai channel Merah (Red)  — sedang untuk kesan cokelat/tanah
            base_b = random.randint(20, 60)     # Nilai channel Biru (Blue)  — rendah agar tidak terlihat biru

            # Isi setiap piksel gambar dengan variasi warna tipis agar terlihat alami (bukan warna solid)
            for r in range(64):         # Iterasi setiap baris piksel (0 sampai 63)
                for c in range(64):     # Iterasi setiap kolom piksel (0 sampai 63)
                    # Tambahkan noise acak ±15 ke setiap channel warna, lalu batasi nilai 0-255
                    img[r, c, 0] = max(0, min(255, base_b + random.randint(-15, 15)))  # Channel B (Biru)
                    img[r, c, 1] = max(0, min(255, base_g + random.randint(-15, 15)))  # Channel G (Hijau)
                    img[r, c, 2] = max(0, min(255, base_r + random.randint(-15, 15)))  # Channel R (Merah)

            filename = f"dummy_organik_{i+1}.png"                           # Beri nama file dummy secara berurutan
            cv2.imwrite(os.path.join(dir_organik, filename), img)           # Simpan gambar ke folder Organik

    # -----------------------------------------------------------------------
    # Generate gambar dummy untuk folder Anorganik
    # -----------------------------------------------------------------------
    # Ambil daftar file gambar yang sudah ada di folder Anorganik
    existing_anorganik = [f for f in os.listdir(dir_anorganik) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    # Jika jumlah gambar yang ada masih kurang dari target, tambahkan gambar dummy
    if len(existing_anorganik) < num_images:
        needed = num_images - len(existing_anorganik)   # Hitung kekurangan gambar
        print(f"Folder Anorganik memiliki {len(existing_anorganik)} gambar. Menambahkan {needed} gambar dummy anorganik...")

        for i in range(needed):
            img = np.zeros((64, 64, 3), dtype=np.uint8)     # Buat kanvas gambar baru 64x64 piksel

            # Pilih secara acak salah satu dari 3 warna dominan anorganik (biru, merah, atau abu-abu)
            tipe = random.choice(["biru", "merah", "abu"])

            if tipe == "biru":      # Plastik biru, kaleng biru, dll.
                base_b = random.randint(150, 240)   # Blue tinggi
                base_g = random.randint(30, 100)    # Green rendah
                base_r = random.randint(30, 100)    # Red rendah
            elif tipe == "merah":   # Kaleng merah, botol merah, dll.
                base_b = random.randint(30, 80)     # Blue rendah
                base_g = random.randint(30, 80)     # Green rendah
                base_r = random.randint(150, 240)   # Red tinggi
            else:                   # Abu-abu (logam, styrofoam, kaca)
                val = random.randint(100, 180)      # Nilai abu-abu tengah
                base_b, base_g, base_r = val, val, val  # Ketiga channel sama = abu-abu

            # Isi setiap piksel dengan variasi warna tipis
            for r in range(64):         # Iterasi setiap baris piksel
                for c in range(64):     # Iterasi setiap kolom piksel
                    img[r, c, 0] = max(0, min(255, base_b + random.randint(-15, 15)))  # Channel B
                    img[r, c, 1] = max(0, min(255, base_g + random.randint(-15, 15)))  # Channel G
                    img[r, c, 2] = max(0, min(255, base_r + random.randint(-15, 15)))  # Channel R

            filename = f"dummy_anorganik_{i+1}.png"                             # Beri nama file dummy
            cv2.imwrite(os.path.join(dir_anorganik, filename), img)             # Simpan gambar ke folder Anorganik


# ==============================================================================
# BAGIAN 2: IMPLEMENTASI DECISION TREE DARI NOL (TANPA LIBRARY ML)
# Terdiri dari: Node (struktur data pohon), fungsi Gini Impurity,
# dan kelas DecisionTreeClassifierScratch (inti algoritma)
# ==============================================================================

class Node:
    """Representasi satu simpul (node) dalam pohon keputusan"""
    def __init__(self, feature_idx=None, threshold=None, left=None, right=None, value=None):
        self.feature_idx = feature_idx  # Indeks fitur yang digunakan untuk memisah data (0=R, 1=G, 2=B)
        self.threshold   = threshold    # Nilai batas (threshold) — data <= threshold masuk kiri, sisanya kanan
        self.left        = left         # Referensi ke node anak cabang kiri (kondisi True)
        self.right       = right        # Referensi ke node anak cabang kanan (kondisi False)
        self.value       = value        # Nilai kelas hasil prediksi — hanya diisi jika node ini adalah daun (leaf)

    def is_leaf(self):
        """Kembalikan True jika node ini adalah daun (tidak punya cabang lagi)"""
        return self.value is not None   # Node adalah daun jika memiliki nilai kelas (value != None)


def calculate_gini(labels):
    """
    Menghitung Gini Impurity dari sekumpulan label kelas.
    Rumus: Gini(D) = 1 - sum(p_i^2)
    Semakin kecil nilai Gini, semakin 'murni' (homogen) kelompok data tersebut.
    """
    if not labels:      # Jika list label kosong, kembalikan 0 (tidak ada ketidakmurnian)
        return 0

    total = len(labels)     # Total jumlah sampel dalam node ini
    counts = {}             # Dictionary untuk menghitung frekuensi setiap kelas

    for label in labels:
        counts[label] = counts.get(label, 0) + 1   # Tambah hitungan untuk setiap kelas yang ditemukan

    # Hitung Gini: 1 dikurangi jumlah kuadrat probabilitas setiap kelas
    gini = 1.0 - sum((count / total) ** 2 for count in counts.values())
    return gini     # Nilai Gini Impurity (0.0 = murni, mendekati 0.5 = paling campur)


class DecisionTreeClassifierScratch:
    """
    Implementasi lengkap algoritma Decision Tree Classifier dari nol.
    Menggunakan Gini Impurity sebagai kriteria pemisahan (splitting criterion).
    Tidak menggunakan library ML apapun (scikit-learn, dll.).
    """
    def __init__(self, max_depth=5, min_samples_split=2):
        self.max_depth         = max_depth          # Kedalaman maksimum pohon — mencegah overfitting
        self.min_samples_split = min_samples_split  # Jumlah sampel minimum agar node bisa dipecah lagi
        self.root              = None               # Node akar pohon, awalnya kosong (diisi setelah fit)

    def fit(self, X, y):
        """Melatih model: membangun pohon keputusan dari data latih X dan label y"""
        self.root = self._build_tree(X, y, depth=0)     # Mulai bangun pohon dari kedalaman 0 (akar)

    def _build_tree(self, X, y, depth):
        """
        Fungsi rekursif untuk membangun pohon keputusan.
        Terus memisah data hingga mencapai kondisi berhenti (stopping criteria).
        """
        num_samples    = len(X)         # Jumlah sampel dalam node saat ini
        if num_samples == 0:            # Jika tidak ada sampel, kembalikan None (node kosong)
            return None

        num_features   = len(X[0])      # Jumlah fitur setiap sampel (dalam kasus ini: 3 fitur RGB)
        unique_classes = set(y)         # Kumpulan kelas unik yang ada dalam node ini

        # Kondisi berhenti rekursi:
        # 1. Sudah mencapai kedalaman maksimum (max_depth)
        # 2. Semua sampel sudah satu kelas (node murni)
        # 3. Jumlah sampel terlalu sedikit untuk dipecah lagi
        if (depth >= self.max_depth or
            len(unique_classes) == 1 or
            num_samples < self.min_samples_split):
            leaf_value = max(unique_classes, key=y.count)   # Pilih kelas terbanyak (majority vote) sebagai hasil daun
            return Node(value=leaf_value)                   # Buat dan kembalikan node daun

        # Cari pembagian (split) terbaik berdasarkan Gini Impurity terendah
        best_idx, best_thresh = self._best_split(X, y, num_features)

        if best_idx is None:    # Jika tidak ada split yang valid ditemukan
            leaf_value = max(unique_classes, key=y.count)   # Buat node daun dengan kelas mayoritas
            return Node(value=leaf_value)

        # Lakukan pemisahan data berdasarkan fitur dan threshold terbaik
        left_X, left_y, right_X, right_y = self._split(X, y, best_idx, best_thresh)

        # Jika salah satu cabang kosong (tidak ada data), buat node daun
        if not left_X or not right_X:
            leaf_value = max(unique_classes, key=y.count)
            return Node(value=leaf_value)

        # Bangun sub-pohon kiri dan kanan secara rekursif (depth + 1 = turun satu level)
        left_child  = self._build_tree(left_X,  left_y,  depth + 1)
        right_child = self._build_tree(right_X, right_y, depth + 1)

        # Buat dan kembalikan node cabang dengan info fitur, threshold, dan kedua anaknya
        return Node(feature_idx=best_idx, threshold=best_thresh, left=left_child, right=right_child)

    def _best_split(self, X, y, num_features):
        """
        Mencari kombinasi fitur + threshold terbaik yang menghasilkan Gini Impurity paling kecil.
        Iterasi semua fitur dan semua calon threshold untuk menemukan pemisah optimal.
        """
        best_gini   = 999.0     # Inisialisasi dengan nilai sangat besar (pasti akan teroverwrite)
        best_idx    = None      # Indeks fitur terbaik (akan diisi saat ditemukan)
        best_thresh = None      # Nilai threshold terbaik (akan diisi saat ditemukan)

        for idx in range(num_features):     # Coba setiap fitur (0=Red, 1=Green, 2=Blue)
            # Ambil semua nilai unik dari fitur ini, lalu urutkan dari kecil ke besar
            values = sorted(list(set(sample[idx] for sample in X)))

            # Hitung calon threshold: titik tengah antara setiap dua nilai berurutan
            thresholds = []
            for i in range(len(values) - 1):
                thresholds.append((values[i] + values[i+1]) / 2.0)     # Rata-rata dua nilai berurutan

            # Jika hanya ada satu nilai unik, gunakan nilai itu sendiri sebagai threshold
            if not thresholds and values:
                thresholds = [values[0]]

            for thresh in thresholds:   # Coba setiap calon threshold
                # Bagi data menjadi dua grup berdasarkan threshold ini
                left_X, left_y, right_X, right_y = self._split(X, y, idx, thresh)

                # Lewati threshold ini jika salah satu cabang kosong (tidak ada data)
                if not left_y or not right_y:
                    continue

                # Hitung Weighted Gini Impurity dari pembagian ini
                p_left   = len(left_y) / len(y)    # Proporsi data yang masuk cabang kiri
                p_right  = len(right_y) / len(y)   # Proporsi data yang masuk cabang kanan
                gini_split = (p_left * calculate_gini(left_y)) + (p_right * calculate_gini(right_y))   # Gini terbobot

                # Simpan jika ini adalah split dengan Gini paling kecil sejauh ini
                if gini_split < best_gini:
                    best_gini   = gini_split    # Update Gini terbaik
                    best_idx    = idx           # Simpan indeks fitur terbaik
                    best_thresh = thresh        # Simpan threshold terbaik

        return best_idx, best_thresh    # Kembalikan fitur & threshold terbaik yang ditemukan

    def _split(self, X, y, feature_idx, threshold):
        """
        Membagi dataset X dan label y menjadi dua grup:
        - Kiri  : sampel dengan nilai fitur[feature_idx] <= threshold
        - Kanan : sampel dengan nilai fitur[feature_idx] >  threshold
        """
        left_X, left_y, right_X, right_y = [], [], [], []  # Inisialisasi 4 list kosong

        for sample, label in zip(X, y):     # Iterasi setiap pasang (data, label)
            if sample[feature_idx] <= threshold:    # Jika nilai fitur <= threshold
                left_X.append(sample)               # Masukkan data ke grup kiri
                left_y.append(label)                # Masukkan label ke grup kiri
            else:                                   # Jika nilai fitur > threshold
                right_X.append(sample)              # Masukkan data ke grup kanan
                right_y.append(label)               # Masukkan label ke grup kanan

        return left_X, left_y, right_X, right_y    # Kembalikan keempat grup hasil pemisahan

    def predict(self, X):
        """Memprediksi kelas untuk sekumpulan data uji (list of samples)"""
        return [self._traverse(sample, self.root) for sample in X]  # Prediksi setiap sampel dengan _traverse

    def _traverse(self, sample, node):
        """
        Menyusuri pohon dari akar hingga daun untuk satu sampel.
        Di setiap node, cek apakah nilai fitur <= threshold, lalu belok kiri atau kanan.
        """
        if node.is_leaf():      # Jika sudah sampai di node daun, kembalikan kelas hasilnya
            return node.value

        if sample[node.feature_idx] <= node.threshold:     # Jika kondisi terpenuhi, belok kiri
            return self._traverse(sample, node.left)
        else:                                               # Jika kondisi tidak terpenuhi, belok kanan
            return self._traverse(sample, node.right)

    def predict_with_path(self, sample, feature_names):
        """
        Memprediksi kelas satu sampel DAN mencatat setiap langkah keputusan yang diambil.
        Berguna untuk menampilkan 'jalur' yang dilalui pohon saat mengklasifikasi gambar.
        """
        path_steps = []         # List untuk menyimpan setiap langkah keputusan
        node = self.root        # Mulai dari node akar

        while not node.is_leaf():   # Terus berjalan selama belum mencapai daun
            feat_name = feature_names[node.feature_idx]    # Ambil nama fitur yang diperiksa
            val       = sample[node.feature_idx]           # Ambil nilai fitur dari sampel uji

            if val <= node.threshold:   # Jika nilai <= threshold, ambil cabang kiri
                path_steps.append(f"Apakah {feat_name} <= {node.threshold:.2f}? (Nilai: {val:.2f}) => [TRUE]")
                node = node.left        # Pindah ke node anak kiri
            else:                       # Jika nilai > threshold, ambil cabang kanan
                path_steps.append(f"Apakah {feat_name} <= {node.threshold:.2f}? (Nilai: {val:.2f}) => [FALSE]")
                node = node.right       # Pindah ke node anak kanan

        return node.value, path_steps  # Kembalikan kelas hasil prediksi + daftar langkah keputusan


# ==============================================================================
# BAGIAN 3: PEMBAGIAN DATA (TRAIN/TEST SPLIT) & EVALUASI KINERJA MODEL
# Semua dihitung manual tanpa sklearn — murni logika Python
# ==============================================================================

def train_test_split_scratch(X, y, test_size=0.2, seed=42):
    """
    Membagi dataset menjadi data latih (train) dan data uji (test).
    test_size=0.2 berarti 20% data digunakan untuk uji, 80% untuk latih.
    """
    random.seed(seed)           # Atur seed agar pembagian selalu konsisten (reproducible)
    combined = list(zip(X, y))  # Gabungkan data dan label menjadi list of tuple agar tidak terpisah saat shuffle
    random.shuffle(combined)    # Acak urutan data agar distribusi merata antara train dan test

    # Hitung indeks pemisah: 80% pertama = train, 20% sisanya = test
    split_idx = int(len(combined) * (1 - test_size))

    # Pisahkan kembali data dan label dari tuple hasil zip
    X_train, y_train = zip(*combined[:split_idx])   # Data dan label latih (80%)
    X_test,  y_test  = zip(*combined[split_idx:])   # Data dan label uji (20%)

    # Kembalikan keempat subset dalam bentuk list (bukan tuple)
    return list(X_train), list(X_test), list(y_train), list(y_test)


def evaluate_performance(y_true, y_pred):
    """
    Menghitung metrik evaluasi model secara manual:
    - Accuracy  : Persentase prediksi yang benar dari keseluruhan data uji
    - Precision : Dari semua yang diprediksi Organik, berapa yang benar-benar Organik?
    - Recall    : Dari semua yang aslinya Organik, berapa yang berhasil dideteksi?
    - F1-Score  : Rata-rata harmonis Precision dan Recall
    - Confusion Matrix: Tabel TP, FP, TN, FN
    """
    total    = len(y_true)                                                  # Total sampel uji
    accuracy = sum(1 for t, p in zip(y_true, y_pred) if t == p) / total    # Hitung akurasi

    # Hitung komponen Confusion Matrix dengan "Organik" sebagai kelas Positif
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == "Organik"   and p == "Organik")    # True Positive
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == "Anorganik" and p == "Organik")    # False Positive
    tn = sum(1 for t, p in zip(y_true, y_pred) if t == "Anorganik" and p == "Anorganik")  # True Negative
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == "Organik"   and p == "Anorganik")  # False Negative

    # Hitung Precision — hindari pembagian nol dengan pengecekan kondisi
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0

    # Hitung Recall (Sensitivity) — hindari pembagian nol
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0

    # Hitung F1-Score — rata-rata harmonis Precision dan Recall
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    # Kembalikan semua metrik dalam bentuk dictionary
    return {
        "accuracy"  : accuracy,
        "precision" : precision,
        "recall"    : recall,
        "f1"        : f1,
        "matrix"    : {"TP": tp, "FP": fp, "TN": tn, "FN": fn}     # Confusion Matrix
    }


# ==============================================================================
# BAGIAN 4: VISUALISASI STRUKTUR POHON KEPUTUSAN DI TERMINAL
# Mencetak pohon secara rekursif dalam bentuk teks bercabang
# ==============================================================================
def print_decision_tree(node, feature_names, depth=0, prefix="Root"):
    """Mencetak struktur pohon keputusan secara visual di terminal dengan indentasi dan warna"""

    if node is None:    # Jika node kosong, langsung keluar (tidak ada yang dicetak)
        return

    indent = "    " * depth     # Indentasi berdasarkan kedalaman — semakin dalam semakin menjorok ke kanan

    if node.is_leaf():  # Jika node ini adalah daun (leaf), cetak hasil akhir klasifikasi
        color = GREEN if node.value == "Organik" else BLUE     # Hijau untuk Organik, Biru untuk Anorganik
        print(f"{indent}\\-- {YELLOW}[Daun]{RESET} {prefix} => {BOLD}HASIL: {color}{node.value}{RESET}")
        return          # Hentikan rekursi — daun tidak punya anak

    # Jika bukan daun, cetak kondisi pemisahan fitur
    feat_name = feature_names[node.feature_idx]     # Ambil nama fitur dari indeksnya
    print(f"{indent}|-- {CYAN}[Cabang]{RESET} {prefix} => JIKA {BOLD}{feat_name} <= {node.threshold:.2f}{RESET}")

    # Rekursi ke cabang kiri (kondisi True: nilai <= threshold)
    print_decision_tree(node.left,  feature_names, depth + 1, f"{GREEN}Kiri (True){RESET}")

    # Rekursi ke cabang kanan (kondisi False: nilai > threshold)
    print_decision_tree(node.right, feature_names, depth + 1, f"{RED}Kanan (False){RESET}")


# ==============================================================================
# BAGIAN 5: ALUR UTAMA PROGRAM (MAIN APPLICATION FLOW)
# Titik masuk program — hanya dijalankan saat file ini dieksekusi langsung
# ==============================================================================
if __name__ == "__main__":

    # Cetak header sambutan program
    print(f"{MAGENTA}+" + "="*78 + f"+{RESET}")
    print(f"{MAGENTA}|{RESET}{BOLD}{YELLOW}{'{:^78}'.format('TUGAS BESAR KECERDASAN BUATAN - DETEKSI SAMPAH MANDIRI')}{RESET}{MAGENTA}|{RESET}")
    print(f"{MAGENTA}|{RESET}{BOLD}{CYAN}{'{:^78}'.format('Sistem Klasifikasi Sampah Berbasis Citra - Decision Tree Custom')}{RESET}{MAGENTA}|{RESET}")
    print(f"{MAGENTA}|{RESET}{'{:^78}'.format('Mendukung Program Pengelolaan Lingkungan Berkelanjutan')}{RESET}{MAGENTA}|{RESET}")
    print(f"{MAGENTA}+" + "="*78 + f"+{RESET}")

    # Tentukan path folder dataset relatif terhadap lokasi file script ini berada
    base_dir     = os.path.dirname(os.path.abspath(__file__))          # Direktori tempat script ini berada
    dir_organik  = os.path.join(base_dir, "dataset", "Organik")        # Path folder gambar Organik
    dir_anorganik = os.path.join(base_dir, "dataset", "Anorganik")     # Path folder gambar Anorganik

    # Buat folder dataset jika belum ada (exist_ok=True agar tidak error jika sudah ada)
    os.makedirs(dir_organik,   exist_ok=True)
    os.makedirs(dir_anorganik, exist_ok=True)

    # Nama-nama fitur yang digunakan (sesuai urutan indeks 0, 1, 2)
    feature_names = [
        "Rerata Warna Merah (Red Mean)",    # Indeks 0 — rata-rata nilai piksel channel Merah
        "Rerata Warna Hijau (Green Mean)",  # Indeks 1 — rata-rata nilai piksel channel Hijau
        "Rerata Warna Biru (Blue Mean)"     # Indeks 2 — rata-rata nilai piksel channel Biru
    ]

    # Inisialisasi list kosong untuk menyimpan fitur (X) dan label (y) dari semua gambar
    X = []  # Berisi list [mean_R, mean_G, mean_B] untuk setiap gambar
    y = []  # Berisi label kelas "Organik" atau "Anorganik" untuk setiap gambar

    print(f"\n{CYAN}>>> Membaca file gambar dan mengekstraksi fitur warna RGB...{RESET}")

    # -----------------------------------------------------------------------
    # Baca dan ekstraksi fitur dari gambar-gambar di folder Organik
    # -----------------------------------------------------------------------
    # Ambil daftar nama file gambar di folder Organik (filter hanya .png, .jpg, .jpeg)
    files_organik = [f for f in os.listdir(dir_organik) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    for file in files_organik:
        img_path = os.path.join(dir_organik, file)  # Buat path lengkap ke file gambar
        img = cv2.imread(img_path)                  # Baca gambar dari disk (format BGR, bukan RGB)

        if img is None:     # Jika gambar gagal dibaca (file rusak/format tidak didukung), lewati
            continue

        img = cv2.resize(img, (64, 64))     # Ubah ukuran gambar menjadi 64x64 piksel agar dimensi seragam

        # Ekstraksi fitur: hitung rata-rata intensitas piksel untuk setiap channel warna
        # Catatan: OpenCV membaca dalam format BGR, bukan RGB
        mean_b = np.mean(img[:, :, 0])     # Rata-rata channel Blue  (indeks 0 di OpenCV)
        mean_g = np.mean(img[:, :, 1])     # Rata-rata channel Green (indeks 1 di OpenCV)
        mean_r = np.mean(img[:, :, 2])     # Rata-rata channel Red   (indeks 2 di OpenCV)

        X.append([mean_r, mean_g, mean_b])  # Simpan fitur RGB ke dalam dataset (urutan R, G, B)
        y.append("Organik")                 # Tandai label gambar ini sebagai Organik

    # -----------------------------------------------------------------------
    # Baca dan ekstraksi fitur dari gambar-gambar di folder Anorganik
    # -----------------------------------------------------------------------
    files_anorganik = [f for f in os.listdir(dir_anorganik) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    for file in files_anorganik:
        img_path = os.path.join(dir_anorganik, file)    # Buat path lengkap ke file gambar
        img = cv2.imread(img_path)                      # Baca gambar dari disk

        if img is None:     # Lewati gambar yang gagal dibaca
            continue

        img = cv2.resize(img, (64, 64))     # Samakan ukuran gambar menjadi 64x64

        # Ekstraksi fitur rata-rata warna RGB (sama seperti proses untuk Organik di atas)
        mean_b = np.mean(img[:, :, 0])      # Rata-rata Blue
        mean_g = np.mean(img[:, :, 1])      # Rata-rata Green
        mean_r = np.mean(img[:, :, 2])      # Rata-rata Red

        X.append([mean_r, mean_g, mean_b])  # Simpan fitur ke dataset
        y.append("Anorganik")               # Tandai label sebagai Anorganik

    # Validasi: pastikan dataset tidak kosong sebelum melanjutkan
    if len(X) == 0:
        print(f"\n{RED}[ERR] Error: Tidak ada gambar yang berhasil dibaca dari dataset!{RESET}")
        sys.exit(1)     # Hentikan program jika tidak ada data sama sekali

    # Tampilkan informasi ringkasan dataset yang berhasil dimuat
    print(f"\n{CYAN}" + "-"*80 + f"{RESET}")
    print(f" {BOLD}INFORMASI DATASET:{RESET}")
    print(f"  > Total gambar terproses : {BOLD}{len(X)}{RESET} sampel")
    print(f"  > Sampah Organik         : {GREEN}{y.count('Organik')}{RESET} sampel")
    print(f"  > Sampah Anorganik       : {BLUE}{y.count('Anorganik')}{RESET} sampel")
    print(f"{CYAN}" + "-"*80 + f"{RESET}")

    # Tampilkan tabel 5 sampel pertama hasil ekstraksi fitur sebagai verifikasi
    print(f"\n{GREEN}[INFO] Menampilkan 5 sampel ekstraksi fitur warna RGB pertama:{RESET}")
    print(f"  {CYAN}+------------------+--------------------+------------------+----------------+{RESET}")
    print(f"  {CYAN}| Rerata Red (X1)  | Rerata Green (X2)  | Rerata Blue (X3) | Kategori Label |{RESET}")
    print(f"  {CYAN}+------------------+--------------------+------------------+----------------+{RESET}")

    for i in range(min(5, len(X))):     # Tampilkan maksimal 5 baris (atau kurang jika data < 5)
        color_label = GREEN if y[i] == "Organik" else BLUE     # Warna label sesuai kategori
        print("  | {:<16.2f} | {:<18.2f} | {:<16.2f} | {}{:<14}{} |".format(
            X[i][0], X[i][1], X[i][2], color_label, y[i], RESET))  # Format tiap baris tabel

    print(f"  {CYAN}+------------------+--------------------+------------------+----------------+{RESET}")

    # Bagi dataset: 80% untuk latih, 20% untuk uji
    X_train, X_test, y_train, y_test = train_test_split_scratch(X, y, test_size=0.2, seed=1)
    print(f"\n{GREEN}[INFO] Pembagian Dataset (Split 80:20):{RESET}")
    print(f"  > Jumlah Data Latih (Train) : {BOLD}{len(X_train)}{RESET} gambar")
    print(f"  > Jumlah Data Uji (Test)    : {BOLD}{len(X_test)}{RESET} gambar")

    # Latih model Decision Tree dari scratch menggunakan data latih
    print(f"\n{CYAN}>>> Melatih Model Decision Tree Custom (Kedalaman Maks = 4)...{RESET}")
    clf = DecisionTreeClassifierScratch(max_depth=4, min_samples_split=2)   # Buat objek Decision Tree
    clf.fit(X_train, y_train)   # Bangun pohon keputusan dari data latih
    print(f"{GREEN}[SUCCESS] Model berhasil dilatih secara mandiri dari nol.{RESET}")

    # Tampilkan struktur pohon keputusan yang terbentuk setelah training
    print("\n" + f"{MAGENTA}="*80 + f"{RESET}")
    print(f"{BOLD}{YELLOW}{'{:^80}'.format('STRUKTUR POHON KEPUTUSAN YANG TERBENTUK (PROSES SELEKSI)')}{RESET}")
    print(f"{MAGENTA}="*80 + f"{RESET}")
    print_decision_tree(clf.root, feature_names)    # Cetak struktur pohon secara rekursif
    print(f"{MAGENTA}="*80 + f"{RESET}")

    # Jalankan prediksi model pada data uji (X_test)
    y_pred  = clf.predict(X_test)                   # Dapatkan prediksi untuk semua data uji
    metrics = evaluate_performance(y_test, y_pred)  # Hitung semua metrik evaluasi

    # Tampilkan laporan evaluasi kinerja model dalam format tabel rapi
    print("\n" + f"{MAGENTA}+" + "="*78 + f"+{RESET}")
    print(f"{MAGENTA}|{RESET}{BOLD}{YELLOW}{'{:^78}'.format('LAPORAN EVALUASI KINERJA MODEL KEPUTUSAN')}{RESET}{MAGENTA}|{RESET}")
    print(f"{MAGENTA}+" + "="*78 + f"+{RESET}")
    print(f"{MAGENTA}|{RESET}  Akurasi Uji (Accuracy)    : {GREEN}{'{:<50.2f}'.format(metrics['accuracy']   * 100)}%{RESET} {MAGENTA}|{RESET}")
    print(f"{MAGENTA}|{RESET}  Presisi Uji (Precision)   : {GREEN}{'{:<50.2f}'.format(metrics['precision']  * 100)}%{RESET} {MAGENTA}|{RESET}")
    print(f"{MAGENTA}|{RESET}  Sensitivitas (Recall)     : {GREEN}{'{:<50.2f}'.format(metrics['recall']     * 100)}%{RESET} {MAGENTA}|{RESET}")
    print(f"{MAGENTA}|{RESET}  Skor Harmoni (F1-Score)   : {GREEN}{'{:<50.2f}'.format(metrics['f1']         * 100)}%{RESET} {MAGENTA}|{RESET}")
    print(f"{MAGENTA}+" + "-"*78 + f"+{RESET}")

    # Tampilkan Confusion Matrix
    matrix = metrics['matrix']
    print(f"{MAGENTA}|{RESET}{BOLD}{CYAN}{'{:^78}'.format('Matriks Kebingungan (Confusion Matrix)')}{RESET}{MAGENTA}|{RESET}")
    print(f"{MAGENTA}+" + "-"*78 + f"+{RESET}")
    print(f"{MAGENTA}|{RESET}                       Prediksi ORGANIK         Prediksi ANORGANIK          {MAGENTA}|{RESET}")
    print(f"{MAGENTA}|{RESET}  Aktual ORGANIK       {GREEN}{'{:<24}'.format(matrix['TP'])}{RESET} {RED}{'{:<27}'.format(matrix['FN'])}{RESET} {MAGENTA}|{RESET}")   # TP = Benar Organik | FN = Salah Anorganik
    print(f"{MAGENTA}|{RESET}  Aktual ANORGANIK     {RED}{'{:<24}'.format(matrix['FP'])}{RESET} {BLUE}{'{:<27}'.format(matrix['TN'])}{RESET} {MAGENTA}|{RESET}")   # FP = Salah Organik | TN = Benar Anorganik
    print(f"{MAGENTA}+" + "="*78 + f"+{RESET}")

    # Tunggu user menekan ENTER sebelum masuk ke modul interaktif
    input(f"\n{YELLOW}Tekan ENTER untuk masuk ke Modul Interaktif...{RESET}")

    # State untuk mengontrol tampilan menu:
    # True  = tampilkan daftar gambar + info menu lengkap (mode utama)
    # False = langsung tampilkan opsi lanjutan saja (setelah klasifikasi selesai)
    tampilkan_daftar = True
    options = []    # Cache daftar gambar yang bisa dipilih user

    # -----------------------------------------------------------------------
    # LOOP UTAMA MODUL INTERAKTIF
    # Program terus berjalan sampai user memilih keluar (X atau pilihan 2)
    # -----------------------------------------------------------------------
    while True:

        # Perbarui daftar gambar setiap iterasi loop (agar gambar baru langsung terdeteksi)
        organik_imgs   = sorted([f for f in os.listdir(dir_organik)   if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        anorganik_imgs = sorted([f for f in os.listdir(dir_anorganik) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])

        # Buat list options berisi tuple (path_lengkap, nama_file, label_folder) untuk setiap gambar
        options = []
        for file in organik_imgs:
            options.append((os.path.join(dir_organik, file), file, "Organik"))      # Gambar dari folder Organik
        for file in anorganik_imgs:
            options.append((os.path.join(dir_anorganik, file), file, "Anorganik"))  # Gambar dari folder Anorganik

        # Tampilkan daftar gambar dan header menu jika dalam mode utama
        if tampilkan_daftar:
            os.system('cls' if os.name == 'nt' else 'clear')   # Bersihkan layar terminal
            print(f"{MAGENTA}={'='*78}={RESET}")
            print(f"{BOLD}{YELLOW}{'{:^80}'.format('MODUL INTERAKTIF KLASIFIKASI CITRA SAMPAH')}{RESET}")
            print(f"{MAGENTA}={'='*78}={RESET}")
            print(f"\n{BOLD}Daftar file gambar terdeteksi dalam dataset:{RESET}")

            # Tampilkan setiap gambar dengan nomor urut
            for idx, (path, name, label) in enumerate(options):
                print("  [{:02d}] {}".format(idx + 1, name))   # Format: [01] nama_file.png

        # Tampilkan instruksi input sesuai state
        if tampilkan_daftar:
            print(f"{MAGENTA}" + "-"*80 + f"{RESET}")
            print(f"{BOLD}{CYAN}Info: Masukkan nomor gambar (1-{len(options)}) untuk mengklasifikasikan, atau [0]/[A]/[C]/[X] untuk opsi lain.{RESET}")
        else:
            print(f"{MAGENTA}" + "-"*80 + f"{RESET}")  # Hanya garis pemisah jika tidak dalam mode daftar

        pilihan = input("Pilih nomor / opsi: ").strip()    # Baca input dari user, hapus spasi di ujung
        if not pilihan:     # Jika user hanya tekan Enter tanpa input, ulangi loop
            continue

        # -----------------------------------------------------------------------
        # OPSI X — Keluar dari program
        # -----------------------------------------------------------------------
        if pilihan.upper() == 'X':
            print("\n" + f"{MAGENTA}+" + "="*78 + f"+{RESET}")
            print(f"{MAGENTA}|{RESET}{BOLD}{GREEN}{'{:^78}'.format('Terima kasih! Tetap semangat menjaga kelestarian lingkungan hidup.')}{RESET}{MAGENTA}|{RESET}")
            print(f"{MAGENTA}+" + "="*78 + f"+{RESET}")
            try:
                cv2.destroyAllWindows()     # Tutup semua jendela OpenCV yang mungkin masih terbuka
            except Exception:
                pass
            break   # Keluar dari while loop → program selesai

        # -----------------------------------------------------------------------
        # OPSI M — Kembali ke tampilan daftar gambar (menu utama)
        # -----------------------------------------------------------------------
        if pilihan.upper() == 'M':
            tampilkan_daftar = True     # Set state agar daftar gambar ditampilkan kembali
            continue

        # -----------------------------------------------------------------------
        # OPSI 0 — Tampilkan slide teori & matematika Decision Tree
        # -----------------------------------------------------------------------
        if pilihan == '0':
            tampilkan_cara_kerja()      # Panggil fungsi tampilkan slide edukasi
            tampilkan_daftar = True     # Setelah slide selesai, kembali ke menu utama
            continue

        # -----------------------------------------------------------------------
        # OPSI C — Uji gambar dari path kustom yang diinput user
        # -----------------------------------------------------------------------
        if pilihan.upper() == 'C':
            os.system('cls' if os.name == 'nt' else 'clear')   # Bersihkan layar
            print(f"{MAGENTA}={'='*78}={RESET}")
            print(f"{BOLD}{YELLOW}{'{:^80}'.format('UJI FILE GAMBAR KUSTOM')}{RESET}")
            print(f"{MAGENTA}={'='*78}={RESET}")
            custom_path = input(f"\nMasukkan jalur file gambar kustom Anda: ").strip()  # Minta path gambar dari user

            # Validasi path: coba berbagai kemungkinan lokasi file
            path_check = custom_path
            if not os.path.exists(path_check):                          # Coba path persis yang diinput
                path_check = os.path.join(base_dir, custom_path)        # Coba relatif terhadap direktori script
            if not os.path.exists(path_check):
                if custom_path.startswith("TUBES/"):                    # Tangani prefix "TUBES/" yang salah
                    path_check = os.path.join(base_dir, custom_path.replace("TUBES/", ""))
                elif custom_path.startswith("TUBES\\"):                 # Tangani prefix "TUBES\" (Windows)
                    path_check = os.path.join(base_dir, custom_path.replace("TUBES\\", ""))

            if not os.path.exists(path_check):  # Jika semua percobaan gagal, tampilkan error
                print(f"{RED}[ERR] File gambar kustom tidak ditemukan pada jalur tersebut!{RESET}")
                tampilkan_daftar = True
                continue

            test_img = cv2.imread(path_check)   # Baca gambar dari path yang valid
            if test_img is None:                # Jika gambar gagal dibaca
                print(f"{RED}[ERR] Gagal memuat file! File rusak atau format tidak didukung.{RESET}")
                tampilkan_daftar = True
                continue

            # Coba tampilkan gambar di jendela GUI OpenCV (jika environment mendukung)
            try:
                cv2.destroyAllWindows()                                     # Tutup jendela lama
                cv2.namedWindow("Citra Sampah Uji", cv2.WINDOW_NORMAL)     # Buat jendela baru yang bisa di-resize
                cv2.imshow("Citra Sampah Uji", test_img)                   # Tampilkan gambar di jendela
                cv2.waitKey(1)                                              # Proses event minimal agar jendela tampil
                print(f"\n[GUI] Membuka jendela visual untuk citra: {os.path.basename(path_check)}")
            except Exception:   # Jika environment tidak mendukung GUI (misalnya server/headless)
                print(f"\n[INFO] Menjalankan sistem headless. Prediksi langsung dicetak.")

            # Ubah ukuran gambar dan ekstraksi fitur RGB
            img_resized = cv2.resize(test_img, (64, 64))    # Samakan ukuran ke 64x64
            tb = np.mean(img_resized[:, :, 0])              # Rata-rata Blue
            tg = np.mean(img_resized[:, :, 1])              # Rata-rata Green
            tr = np.mean(img_resized[:, :, 2])              # Rata-rata Red

            fitur_uji = [tr, tg, tb]    # Susun fitur dalam urutan [R, G, B]

            # Klasifikasi gambar dan dapatkan jalur keputusan pohon
            kategori_prediksi, path_steps = clf.predict_with_path(fitur_uji, feature_names)

            # Tampilkan nilai fitur yang diekstrak dan jalur keputusan pohon
            print(f"\n{CYAN}>>> Rerata RGB yang Diekstrak:{RESET} R={tr:.2f}, G={tg:.2f}, B={tb:.2f}")
            print(f"{YELLOW}>>> Alur Keputusan Decision Tree:{RESET}")

            for step_idx, step in enumerate(path_steps):   # Tampilkan setiap langkah keputusan
                if "=> [TRUE]" in step:
                    formatted_step = step.replace("=> [TRUE]",  f"=> {GREEN}TRUE (Belok Kiri){RESET}")    # Warnai TRUE
                else:
                    formatted_step = step.replace("=> [FALSE]", f"=> {RED}FALSE (Belok Kanan){RESET}")   # Warnai FALSE
                print(f"    Langkah {step_idx+1}: {formatted_step}")

            # Tampilkan hasil klasifikasi dan rekomendasi pengelolaan
            color_pred = GREEN if kategori_prediksi == "Organik" else BLUE  # Pilih warna sesuai hasil prediksi
            print(f"\n{color_pred}+" + "-"*68 + f"+{RESET}")
            print(f"{color_pred}|{RESET}{BOLD}{'{:^68}'.format('HASIL KLASIFIKASI CITRA SAMPAH KUSTOM')}{RESET}{color_pred}|{RESET}")
            print(f"{color_pred}+" + "-"*68 + f"+{RESET}")
            print(f"{color_pred}|{RESET}  Nama File    : {BOLD}{'{:<48}'.format(os.path.basename(path_check))}{RESET} {color_pred}|{RESET}")
            print(f"{color_pred}|{RESET}  Kategori     : {BOLD}{color_pred}{'{:<48}'.format(kategori_prediksi.upper())}{RESET} {color_pred}|{RESET}")
            print(f"{color_pred}+" + "-"*68 + f"+{RESET}")
            print(f"{color_pred}|{RESET}{BOLD}{'{:^68}'.format('REKOMENDASI PENGELOLAAN YANG DISARANKAN')}{RESET}{color_pred}|{RESET}")
            print(f"{color_pred}+" + "-"*68 + f"+{RESET}")

            if kategori_prediksi == "Organik":      # Rekomendasi khusus untuk sampah Organik
                print(f"{color_pred}|{RESET}  - Lakukan pengomposan (Composting) untuk pupuk tanaman            {color_pred}|{RESET}")
                print(f"{color_pred}|{RESET}  - Gunakan sebagai media pakan budidaya maggot BSF (Black Soldier)   {color_pred}|{RESET}")
                print(f"{color_pred}|{RESET}  - Olah menjadi cairan Eco-Enzyme serbaguna alami                   {color_pred}|{RESET}")
            else:                                   # Rekomendasi khusus untuk sampah Anorganik
                print(f"{color_pred}|{RESET}  - Pisahkan sesuai bahan (Plastik, Logam, Kertas, Kaca)             {color_pred}|{RESET}")
                print(f"{color_pred}|{RESET}  - Setorkan ke Bank Sampah terdekat agar didaur ulang               {color_pred}|{RESET}")
                print(f"{color_pred}|{RESET}  - Hindari membakar plastik demi kesehatan pernapasan               {color_pred}|{RESET}")
            print(f"{color_pred}+" + "-"*68 + f"+{RESET}")

            tampilkan_daftar = False    # Setelah klasifikasi, cukup tampilkan opsi lanjutan saja
            continue

        # -----------------------------------------------------------------------
        # OPSI ANGKA / A — Pilih gambar dari daftar (single, range, atau semua)
        # -----------------------------------------------------------------------
        valid_indices = []  # List indeks gambar yang dipilih user (0-indexed)

        if pilihan.upper() == 'A':      # 'A' = pilih semua gambar sekaligus
            valid_indices = list(range(len(options)))

        else:   # Proses input angka: bisa tunggal (misal: "3"), pisah koma (misal: "1,3,5"), atau range (misal: "2-5")
            chosen_numbers = []
            parts = pilihan.split(",")  # Pisah input berdasarkan koma untuk multi-pilih

            for part in parts:
                part = part.strip()     # Hapus spasi di setiap bagian
                if not part:
                    continue            # Lewati bagian kosong

                if "-" in part:         # Jika mengandung "-", coba parse sebagai rentang (range)
                    subparts = part.split("-")
                    if len(subparts) == 2 and subparts[0].strip().isdigit() and subparts[1].strip().isdigit():
                        start = int(subparts[0].strip())    # Nomor awal range
                        end   = int(subparts[1].strip())    # Nomor akhir range
                        if start <= end:
                            chosen_numbers.extend(range(start, end + 1))        # Range naik
                        else:
                            chosen_numbers.extend(range(start, end - 1, -1))    # Range turun
                    else:
                        print(f"{RED}[WARN] Format rentang '{part}' tidak valid!{RESET}")  # Format range salah
                elif part.isdigit():            # Jika angka tunggal
                    chosen_numbers.append(int(part))
                else:
                    print(f"{RED}[WARN] Format '{part}' tidak dikenali!{RESET}")   # Input tidak dikenal

            # Validasi setiap nomor yang dipilih: harus dalam rentang 1 s.d. jumlah gambar
            for num in chosen_numbers:
                if 1 <= num <= len(options):
                    valid_indices.append(num - 1)   # Konversi ke 0-indexed
                else:
                    print(f"{RED}[WARN] Nomor gambar [{num:02d}] di luar jangkauan (1-{len(options)})!{RESET}")

        # Jika tidak ada gambar valid yang dipilih, minta user mencoba lagi
        if not valid_indices:
            print(f"{RED}[WARN] Tidak ada gambar valid yang dipilih. Silakan coba lagi.{RESET}")
            continue

        # -----------------------------------------------------------------------
        # PROSES KLASIFIKASI UNTUK SEMUA GAMBAR YANG DIPILIH
        # -----------------------------------------------------------------------
        for rank, idx in enumerate(valid_indices):
            selected_path, name, label = options[idx]   # Ambil info gambar: path, nama, dan label folder

            # Cetak header pemrosesan gambar ini
            print(f"\n{BOLD}{MAGENTA}" + "-"*80 + f"{RESET}")
            print(f"{BOLD}{YELLOW}  MEMPROSES CITRA [{rank+1}/{len(valid_indices)}]: {name}{RESET}")
            print(f"{BOLD}{MAGENTA}" + "-"*80 + f"{RESET}")

            test_img = cv2.imread(selected_path)    # Baca gambar dari path
            if test_img is None:                    # Lewati jika gagal dibaca
                print(f"{RED}[ERR] File '{name}' gagal dibaca!{RESET}")
                continue

            # Coba tampilkan gambar di jendela GUI
            try:
                cv2.destroyAllWindows()                                     # Tutup jendela sebelumnya
                cv2.namedWindow("Citra Sampah Uji", cv2.WINDOW_NORMAL)     # Buat jendela baru
                cv2.imshow("Citra Sampah Uji", test_img)                   # Tampilkan gambar
                cv2.waitKey(1)                                              # Proses event agar jendela tampil
                print(f"[GUI] Menampilkan jendela '{name}'...")
            except Exception:
                print("[INFO] Menjalankan sistem headless (tanpa GUI).")    # Fallback jika tidak ada GUI

            # Ubah ukuran gambar dan ekstraksi fitur RGB
            img_resized = cv2.resize(test_img, (64, 64))    # Samakan ukuran ke 64x64
            tb = np.mean(img_resized[:, :, 0])              # Rata-rata Blue
            tg = np.mean(img_resized[:, :, 1])              # Rata-rata Green
            tr = np.mean(img_resized[:, :, 2])              # Rata-rata Red

            fitur_uji = [tr, tg, tb]    # Susun vektor fitur [R, G, B]

            # Klasifikasi gambar dan dapatkan jalur keputusan
            kategori_prediksi, path_steps = clf.predict_with_path(fitur_uji, feature_names)

            # Tampilkan nilai fitur dan jalur keputusan pohon
            print(f"\n{CYAN}>>> Rerata RGB yang Diekstrak:{RESET} R={tr:.2f}, G={tg:.2f}, B={tb:.2f}")
            print(f"{YELLOW}>>> Alur Keputusan Decision Tree:{RESET}")

            for step_idx, step in enumerate(path_steps):   # Tampilkan setiap langkah keputusan
                if "=> [TRUE]" in step:
                    formatted_step = step.replace("=> [TRUE]",  f"=> {GREEN}TRUE (Belok Kiri){RESET}")
                else:
                    formatted_step = step.replace("=> [FALSE]", f"=> {RED}FALSE (Belok Kanan){RESET}")
                print(f"    Langkah {step_idx+1}: {formatted_step}")

            # Tampilkan kotak hasil klasifikasi dan rekomendasi pengelolaan
            color_pred = GREEN if kategori_prediksi == "Organik" else BLUE
            print(f"\n{color_pred}+" + "-"*68 + f"+{RESET}")
            print(f"{color_pred}|{RESET}{BOLD}{'{:^68}'.format('HASIL KLASIFIKASI CITRA SAMPAH')}{RESET}{color_pred}|{RESET}")
            print(f"{color_pred}+" + "-"*68 + f"+{RESET}")
            print(f"{color_pred}|{RESET}  Nama File    : {BOLD}{'{:<48}'.format(name)}{RESET} {color_pred}|{RESET}")
            print(f"{color_pred}|{RESET}  Kategori     : {BOLD}{color_pred}{'{:<48}'.format(kategori_prediksi.upper())}{RESET} {color_pred}|{RESET}")
            print(f"{color_pred}+" + "-"*68 + f"+{RESET}")
            print(f"{color_pred}|{RESET}{BOLD}{'{:^68}'.format('REKOMENDASI PENGELOLAAN YANG DISARANKAN')}{RESET}{color_pred}|{RESET}")
            print(f"{color_pred}+" + "-"*68 + f"+{RESET}")

            if kategori_prediksi == "Organik":
                print(f"{color_pred}|{RESET}  - Lakukan pengomposan (Composting) untuk pupuk tanaman            {color_pred}|{RESET}")
                print(f"{color_pred}|{RESET}  - Gunakan sebagai media pakan budidaya maggot BSF (Black Soldier)   {color_pred}|{RESET}")
                print(f"{color_pred}|{RESET}  - Olah menjadi cairan Eco-Enzyme serbaguna alami                   {color_pred}|{RESET}")
            else:
                print(f"{color_pred}|{RESET}  - Pisahkan sesuai bahan (Plastik, Logam, Kertas, Kaca)             {color_pred}|{RESET}")
                print(f"{color_pred}|{RESET}  - Setorkan ke Bank Sampah terdekat agar didaur ulang               {color_pred}|{RESET}")
                print(f"{color_pred}|{RESET}  - Hindari membakar plastik demi kesehatan pernapasan               {color_pred}|{RESET}")
            print(f"{color_pred}+" + "-"*68 + f"+{RESET}")

            # Jika batch mode dan masih ada gambar berikutnya, beri jeda sebelum lanjut
            if len(valid_indices) > 1 and rank < len(valid_indices) - 1:
                input(f"\n{YELLOW}Tekan ENTER untuk memproses gambar berikutnya [{rank+2}/{len(valid_indices)}]...{RESET}")

        # -----------------------------------------------------------------------
        # Setelah semua gambar selesai diproses, tampilkan pilihan lanjutan
        # -----------------------------------------------------------------------
        print(f"\n{BOLD}  [1]{RESET} Lanjut pilih gambar lain")   # Opsi kembali ke daftar gambar
        print(f"  {BOLD}[2]{RESET} Stop & Keluar program")         # Opsi keluar program
        print(f"{MAGENTA}" + "-"*80 + f"{RESET}")

        # Loop kecil untuk memastikan user memasukkan pilihan yang valid (1 atau 2)
        while True:
            lanjut = input("Pilihan (1/2): ").strip()   # Baca pilihan user

            if lanjut == "1":           # User ingin memilih gambar lain
                tampilkan_daftar = True # Kembali ke mode daftar gambar
                break                   # Keluar dari loop kecil, lanjutkan loop utama

            elif lanjut == "2":         # User ingin keluar dari program
                print("\n" + f"{MAGENTA}+" + "="*78 + f"+{RESET}")
                print(f"{MAGENTA}|{RESET}{BOLD}{GREEN}{'{:^78}'.format('Terima kasih! Tetap semangat menjaga kelestarian lingkungan hidup.')}{RESET}{MAGENTA}|{RESET}")
                print(f"{MAGENTA}+" + "="*78 + f"+{RESET}")
                try:
                    cv2.destroyAllWindows()     # Tutup semua jendela OpenCV
                except Exception:
                    pass
                import sys          # Import sys untuk memanggil sys.exit()
                sys.exit(0)         # Keluar dari program dengan kode sukses (0)

            else:   # Input tidak valid
                print(f"{RED}[WARN] Masukkan 1 untuk lanjut atau 2 untuk stop.{RESET}")
