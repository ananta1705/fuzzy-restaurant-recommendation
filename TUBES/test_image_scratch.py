# ==============================================================================
# KLASIFIKASI GAMBAR SAMPAH ORGANIK DAN ANORGANIK
# Metode: Decision Tree From Scratch (Tanpa Library ML)
# Kelompok 5 - Tugas Besar Kecerdasan Buatan
# ==============================================================================

import os  # Modul untuk operasi sistem file
import cv2  # Modul OpenCV untuk pemrosesan citra
import numpy as np  # Modul NumPy untuk pengolahan array/matriks
import random  # Modul random untuk pengacakan data
import sys  # Modul sys untuk konfigurasi sistem Python

# Aktifkan warna ANSI di terminal Windows
if sys.platform.startswith('win'):  # Periksa jika sistem operasi Windows
    os.system('color')  # Aktifkan warna ANSI di terminal

# Kode warna ANSI
GREEN     = "\033[1;32m"  # Warna hijau tebal
BLUE      = "\033[1;34m"  # Warna biru tebal
YELLOW    = "\033[1;33m"  # Warna kuning tebal
RED       = "\033[1;31m"  # Warna merah tebal
CYAN      = "\033[1;36m"  # Warna cyan tebal
MAGENTA   = "\033[1;35m"  # Warna magenta tebal
RESET     = "\033[0m"  # Reset formatting warna
BOLD      = "\033[1m"  # Format teks tebal
UNDERLINE = "\033[4m"  # Format teks garis bawah


# ==============================================================================
# BAGIAN 1: IMPLEMENTASI DECISION TREE DARI NOL (TANPA LIBRARY ML)
# ==============================================================================

class Node:  # Definisi kelas Node pohon keputusan
    """Satu simpul dalam pohon keputusan"""
    def __init__(self, feature_idx=None, threshold=None, left=None, right=None, value=None):  # Inisialisasi node
        self.feature_idx = feature_idx  # Indeks fitur (0=R, 1=G, 2=B)
        self.threshold   = threshold    # Nilai batas pemisah
        self.left        = left         # Cabang kiri (nilai <= threshold)
        self.right       = right        # Cabang kanan (nilai > threshold)
        self.value       = value        # Kelas hasil (hanya pada node daun)

    def is_leaf(self):  # Cek jika node adalah daun
        return self.value is not None  # Return True jika memiliki kelas hasil


# Hitung nilai Gini Impurity
def calculate_gini(labels): # labels = list of class labels in the node (misal: ["Organik", "Organik", "Anorganik"])
    if not labels:  # Cek jika data kosong
        return 0  # Gini minimum jika kosong

    total = len(labels) # Total sampel di node
    counts = {}  # Dictionary hitung frekuensi label
    for label in labels:  # Loop setiap label
        counts[label] = counts.get(label, 0) + 1 # Hitung jumlah sampel per kelas

    gini = 1.0 - sum((count / total) ** 2 for count in counts.values()) # Gini = 1 - sum(p_i^2) di mana p_i adalah proporsi kelas i ``
    return gini  # Kembalikan nilai Gini


class DecisionTreeClassifierScratch:  # Kelas Decision Tree Classifier
    """Decision Tree Classifier dari nol, menggunakan Gini Impurity"""
    def __init__(self, max_depth=5, min_samples_split=2):  # Inisialisasi parameter model
        self.max_depth         = max_depth  # Kedalaman maksimal pohon
        self.min_samples_split = min_samples_split  # Minimum sampel untuk split
        self.root              = None  # Node akar awal

    def fit(self, X, y):  # Fungsi latih model
        """Bangun pohon dari data latih"""
        self.root = self._build_tree(X, y, depth=0)  # Memulai pembuatan pohon

    def _build_tree(self, X, y, depth):  # Bangun pohon rekursif
        """Rekursif: bangun pohon hingga kondisi berhenti terpenuhi"""
        num_samples    = len(X)  # Jumlah total sampel
        if num_samples == 0:  # Jika sampel kosong
            return None  # Kembalikan None

        num_features   = len(X[0])  # Jumlah total fitur (misal: 3 untuk R, G, B)
        unique_classes = set(y)  # Himpunan kelas unik di node ini (misal: {"Organik", "Anorganik"})

        # Kondisi berhenti: max depth, node murni, atau sampel terlalu sedikit
        if (depth >= self.max_depth or  # Jika sudah mencapai batas kedalaman
            len(unique_classes) == 1 or  # Jika kelas sudah murni
            num_samples < self.min_samples_split):  # Jika sampel kurang dari batas split
            leaf_value = max(unique_classes, key=y.count)  # Gunakan kelas terbanyak
            return Node(value=leaf_value)  # Kembalikan node daun

        # Cari split terbaik berdasarkan Gini terendah
        best_idx, best_thresh = self._best_split(X, y, num_features)  # Cari fitur & threshold terbaik

        if best_idx is None:  # Jika split terbaik tidak ada
            leaf_value = max(unique_classes, key=y.count)  # Kelas mayoritas
            return Node(value=leaf_value)  # Buat node daun

        left_X, left_y, right_X, right_y = self._split(X, y, best_idx, best_thresh)  # Lakukan split data

        if not left_X or not right_X:  # Jika salah satu cabang split kosong
            leaf_value = max(unique_classes, key=y.count)  # Kelas mayoritas
            return Node(value=leaf_value)  # Buat node daun

        left_child  = self._build_tree(left_X,  left_y,  depth + 1)  # Bangun sub-pohon cabang kiri
        right_child = self._build_tree(right_X, right_y, depth + 1)  # Bangun sub-pohon cabang kanan

        return Node(feature_idx=best_idx, threshold=best_thresh, left=left_child, right=right_child)  # Return node cabang

    def _best_split(self, X, y, num_features):  # Cari split terbaik
        """Cari fitur + threshold dengan Gini Impurity terkecil"""
        best_gini   = 999.0  # Inisialisasi Gini terkecil awal
        best_idx    = None  # Indeks fitur terbaik
        best_thresh = None  # Nilai threshold terbaik

        for idx in range(num_features):  # Loop setiap kolom fitur
            values = sorted(list(set(sample[idx] for sample in X)))  # Daftar nilai unik terurut

            # Kandidat threshold: titik tengah antar nilai berurutan
            thresholds = []  # List kandidat threshold
            for i in range(len(values) - 1):  # Loop nilai unik
                thresholds.append((values[i] + values[i+1]) / 2.0)  # Hitung titik tengah

            if not thresholds and values:  # Cek jika tidak ada kandidat threshold
                thresholds = [values[0]]  # Gunakan nilai pertama yang ada

            for thresh in thresholds:  # Uji setiap kandidat threshold
                left_X, left_y, right_X, right_y = self._split(X, y, idx, thresh)  # Split data sementara

                if not left_y or not right_y:  # Lewati jika split menghasilkan cabang kosong
                    continue  # Lanjut ke threshold berikutnya

                # Hitung Weighted Gini
                p_left     = len(left_y) / len(y)  # Rasio data cabang kiri
                p_right    = len(right_y) / len(y)  # Rasio data cabang kanan
                gini_split = (p_left * calculate_gini(left_y)) + (p_right * calculate_gini(right_y))  # Nilai Gini split

                if gini_split < best_gini:  # Cek jika nilai Gini split lebih kecil
                    best_gini   = gini_split  # Simpan nilai Gini split terkecil
                    best_idx    = idx  # Simpan indeks fitur terbaik
                    best_thresh = thresh  # Simpan threshold terbaik

        return best_idx, best_thresh  # Kembalikan fitur & threshold terbaik

    def _split(self, X, y, feature_idx, threshold):  # Fungsi split data
        """Pisah data ke cabang kiri (<= threshold) dan kanan (> threshold)"""
        left_X, left_y, right_X, right_y = [], [], [], []  # Inisialisasi penampung data split

        for sample, label in zip(X, y):  # Loop setiap sampel dan label
            if sample[feature_idx] <= threshold:  # Masuk ke cabang kiri
                left_X.append(sample)  # Tambahkan fitur ke kiri
                left_y.append(label)  # Tambahkan label ke kiri
            else:  # Masuk ke cabang kanan
                right_X.append(sample)  # Tambahkan fitur ke kanan
                right_y.append(label)  # Tambahkan label ke kanan

        return left_X, left_y, right_X, right_y  # Kembalikan hasil split data

    def predict(self, X):  # Fungsi prediksi sekumpulan sampel
        """Prediksi kelas untuk sekumpulan sampel"""
        return [self._traverse(sample, self.root) for sample in X]  # Traverse pohon untuk setiap sampel

    def _traverse(self, sample, node):  # Traversal rekursif pohon
        """Susuri pohon dari akar hingga daun untuk satu sampel"""
        if node.is_leaf():  # Jika sampai pada node daun
            return node.value  # Kembalikan label kelas daun

        if sample[node.feature_idx] <= node.threshold:  # Cek percabangan kiri
            return self._traverse(sample, node.left)  # Telusuri cabang kiri
        else:  # Cek percabangan kanan
            return self._traverse(sample, node.right)  # Telusuri cabang kanan

    def predict_with_path(self, sample, feature_names):  # Prediksi dan rekam rute
        """Prediksi kelas dan catat jalur keputusan pohon"""
        path_steps = []  # List perekam rute keputusan
        node = self.root  # Mulai dari node akar

        while not node.is_leaf():  # Loop sampai mencapai node daun
            feat_name = feature_names[node.feature_idx]  # Nama fitur aktif
            val       = sample[node.feature_idx]  # Nilai fitur sampel

            if val <= node.threshold:  # Rute kiri
                path_steps.append(f"Apakah {feat_name} <= {node.threshold:.2f}? (Nilai: {val:.2f}) => [TRUE]")  # Catat rute True
                node = node.left  # Pindah ke node anak kiri
            else:  # Rute kanan
                path_steps.append(f"Apakah {feat_name} <= {node.threshold:.2f}? (Nilai: {val:.2f}) => [FALSE]")  # Catat rute False
                node = node.right  # Pindah ke node anak kanan

        return node.value, path_steps  # Kembalikan nilai kelas & rute keputusan


# ==============================================================================
# BAGIAN 2: TRAIN/TEST SPLIT & EVALUASI MODEL
# ==============================================================================

# Bagi dataset menjadi data latih dan data uji
def train_test_split_scratch(X, y, test_size=0.2, seed=42):  # Split dataset buatan sendiri
    random.seed(seed)  # Set seed acak
    combined = list(zip(X, y))  # Gabungkan X dan y
    random.shuffle(combined)  # Acak urutan gabungan data

    split_idx = int(len(combined) * (1 - test_size))  # Hitung indeks batas split

    X_train, y_train = zip(*combined[:split_idx])   # 80% latih
    X_test,  y_test  = zip(*combined[split_idx:])   # 20% uji

    return list(X_train), list(X_test), list(y_train), list(y_test)  # Kembalikan data split


# Hitung metrik evaluasi: Accuracy, Precision, Recall, F1, Confusion Matrix
def evaluate_performance(y_true, y_pred):  # Hitung performa model
    total    = len(y_true)  # Dapatkan jumlah data aktual
    accuracy = sum(1 for t, p in zip(y_true, y_pred) if t == p) / total  # Hitung akurasi

    # Confusion Matrix (Organik = kelas Positif)
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == "Organik"   and p == "Organik")  # True Positive
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == "Anorganik" and p == "Organik")  # False Positive
    tn = sum(1 for t, p in zip(y_true, y_pred) if t == "Anorganik" and p == "Anorganik")  # True Negative
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == "Organik"   and p == "Anorganik")  # False Negative

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0  # Hitung presisi
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0  # Hitung recall
    f1        = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0  # Hitung F1-score

    return {  # Kembalikan dictionary metrik evaluasi
        "accuracy"  : accuracy,
        "precision" : precision,
        "recall"    : recall,
        "f1"        : f1,
        "matrix"    : {"TP": tp, "FP": fp, "TN": tn, "FN": fn}
    }


# ==============================================================================
# BAGIAN 3: VISUALISASI POHON KEPUTUSAN DI TERMINAL
# ==============================================================================

# Cetak struktur pohon secara rekursif
def print_decision_tree(node, feature_names, depth=0, prefix="Root"):  # Print struktur pohon keputusan
    if node is None:  # Cek jika node kosong
        return  # Hentikan cetak

    indent = "    " * depth  # Tentukan spasi indentasi level depth

    if node.is_leaf():  # Cek jika node daun
        color = GREEN if node.value == "Organik" else BLUE  # Tentukan warna kelas
        print(f"{indent}\\-- {YELLOW}[Daun]{RESET} {prefix} => {BOLD}HASIL: {color}{node.value}{RESET}")  # Print daun
        return  # Keluar dari rekursi cabang daun

    feat_name = feature_names[node.feature_idx]  # Nama fitur node cabang
    print(f"{indent}|-- {CYAN}[Cabang]{RESET} {prefix} => JIKA {BOLD}{feat_name} <= {node.threshold:.2f}{RESET}")  # Print cabang

    print_decision_tree(node.left,  feature_names, depth + 1, f"{GREEN}Kiri (True){RESET}")  # Cetak cabang kiri
    print_decision_tree(node.right, feature_names, depth + 1, f"{RED}Kanan (False){RESET}")  # Cetak cabang kanan


# ==============================================================================
# BAGIAN 4: ALUR UTAMA PROGRAM
# ==============================================================================
if __name__ == "__main__":  # Cek run utama

    # Header program
    print("=" * 60)  # Print garis atas
    print("TUGAS BESAR KECERDASAN BUATAN")  # Print judul tugas besar
    print("Klasifikasi Sampah Organik dan Anorganik")  # Print judul klasifikasi
    print("Metode : Decision Tree")  # Print keterangan metode
    print("=" * 60)  # Print pembatas tengah
    print("Kelompok 5")  # Print nomor kelompok
    print("Ananta Puti Maharani")  # Print nama kelompok
    print("Marta Safitri")  # Print nama kelompok
    print("=" * 60)  # Print garis bawah

    # Tentukan path folder dataset relatif terhadap lokasi file script ini berada
    base_dir     = os.path.dirname(os.path.abspath(__file__))          # Direktori tempat script ini berada      
    dir_organik  = os.path.join(base_dir, "dataset", "Organik")        # Path folder gambar Organik
    dir_anorganik = os.path.join(base_dir, "dataset", "Anorganik")     # Path folder gambar Anorganik

    # Buat folder dataset jika belum ada (exist_ok=True agar tidak error jika sudah ada)
    os.makedirs(dir_organik,   exist_ok=True)  # Buat direktori organik
    os.makedirs(dir_anorganik, exist_ok=True)  # Buat direktori anorganik

    # Nama-nama fitur yang digunakan (sesuai urutan indeks 0, 1, 2) 
    feature_names = [
        "Rerata Warna Merah (Red Mean)",    # Indeks 0 — rata-rata nilai piksel channel Merah
        "Rerata Warna Hijau (Green Mean)",  # Indeks 1 — rata-rata nilai piksel channel Hijau
        "Rerata Warna Biru (Blue Mean)"     # Indeks 2 — rata-rata nilai piksel channel Biru
    ]

    # Inisialisasi list kosong untuk menyimpan fitur (X) dan label (y) dari semua gambar
    X = []  # Berisi list [mean_R, mean_G, mean_B] untuk setiap gambar
    y = []  # Berisi label kelas "Organik" atau "Anorganik" untuk setiap gambar

    print(f"\n{CYAN}>>> Membaca file gambar dan mengekstraksi fitur warna RGB...{RESET}")  # Print info mulai baca data

    # -----------------------------------------------------------------------
    # Baca dan ekstraksi fitur dari gambar-gambar di folder Organik
    # -----------------------------------------------------------------------
    # Ambil gambar organik
    files_organik = [f for f in os.listdir(dir_organik) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]  # List file gambar organik

    for file in files_organik:  # Loop setiap file organik
        img_path = os.path.join(dir_organik, file)  # Buat path lengkap ke file gambar
        img = cv2.imread(img_path)                  # Baca gambar dari disk (format BGR, bukan RGB)

        if img is None:     # Jika gambar gagal dibaca (file rusak/format tidak didukung), lewati
            continue  # Lewati jika gagal membaca gambar

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
    # Ambil gambar anorganik
    files_anorganik = [f for f in os.listdir(dir_anorganik) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]  # List file gambar anorganik

    for file in files_anorganik:  # Loop setiap file anorganik
        img_path = os.path.join(dir_anorganik, file)    # Buat path lengkap ke file gambar
        img = cv2.imread(img_path)                      # Baca gambar dari disk

        if img is None:     # Lewati gambar yang gagal dibaca
            continue  # Lewati jika gambar gagal dibaca

        img = cv2.resize(img, (64, 64))     # Samakan ukuran gambar menjadi 64x64

        # Ekstraksi fitur rata-rata warna RGB (sama seperti proses untuk Organik di atas)
        mean_b = np.mean(img[:, :, 0])      # Rata-rata Blue
        mean_g = np.mean(img[:, :, 1])      # Rata-rata Green
        mean_r = np.mean(img[:, :, 2])      # Rata-rata Red

        X.append([mean_r, mean_g, mean_b])  # Simpan fitur ke dataset
        y.append("Anorganik")               # Tandai label sebagai Anorganik

    # Validasi: pastikan dataset tidak kosong sebelum melanjutkan
    if len(X) == 0:  # Cek jika dataset kosong
        print(f"\n{RED}[ERR] Error: Tidak ada gambar yang berhasil dibaca dari dataset!{RESET}")  # Print pesan error kosong
        sys.exit(1)     # Hentikan program jika tidak ada data sama sekali

    # Tampilkan informasi dataset
    print(f"\n{CYAN}" + "-"*60 + f"{RESET}")  # Print garis pemisah
    print(f" {BOLD}INFORMASI DATASET:{RESET}")  # Print sub-judul dataset info
    print(f"  Total Data  : {BOLD}{len(X)}{RESET} sampel")  # Print jumlah sampel total
    print(f"  Organik     : {GREEN}{y.count('Organik')}{RESET} sampel")  # Print jumlah organik
    print(f"  Anorganik   : {BLUE}{y.count('Anorganik')}{RESET} sampel")  # Print jumlah anorganik
    print(f"{CYAN}" + "-"*60 + f"{RESET}")  # Print garis pemisah

    # Tampilkan 5 sampel pertama
    print(f"\n{GREEN}[INFO] Menampilkan 5 sampel ekstraksi fitur warna RGB pertama:{RESET}")  # Print info pembuka tabel
    print(f"  {CYAN}+------------------+--------------------+------------------+----------------+{RESET}")  # Print baris pembatas tabel
    print(f"  {CYAN}| Rerata Red (X1)  | Rerata Green (X2)  | Rerata Blue (X3) | Kategori Label |{RESET}")  # Print header kolom tabel
    print(f"  {CYAN}+------------------+--------------------+------------------+----------------+{RESET}")  # Print baris pembatas kolom

    for i in range(min(5, len(X))):     # Tampilkan maksimal 5 baris (atau kurang jika data < 5)
        color_label = GREEN if y[i] == "Organik" else BLUE     # Warna label sesuai kategori
        print("  | {:<16.2f} | {:<18.2f} | {:<16.2f} | {}{:<14}{} |".format(
            X[i][0], X[i][1], X[i][2], color_label, y[i], RESET))  # Format tiap baris tabel

    print(f"  {CYAN}+------------------+--------------------+------------------+----------------+{RESET}")  # Print pembatas bawah tabel

    # Bagi dataset: 80% untuk latih, 20% untuk uji
    X_train, X_test, y_train, y_test = train_test_split_scratch(X, y, test_size=0.2, seed=344)  # Split dataset
    print(f"\n{GREEN}[INFO] Pembagian Dataset (Split 80:20):{RESET}")  # Print info split dataset
    print(f"  > Jumlah Data Latih (Train) : {BOLD}{len(X_train)}{RESET} gambar")  # Print total data latih
    print(f"  > Jumlah Data Uji (Test)    : {BOLD}{len(X_test)}{RESET} gambar")  # Print total data uji

    # Latih model Decision Tree dari scratch menggunakan data latih
    print(f"\n{CYAN}>>> Melatih Model Decision Tree Custom (Kedalaman Maks = 5)...{RESET}")  # Print status training model
    clf = DecisionTreeClassifierScratch(max_depth=5, min_samples_split=2)   # Buat objek Decision Tree
    clf.fit(X_train, y_train)   # Bangun pohon keputusan dari data latih
    print(f"{GREEN}[SUCCESS] Model berhasil dilatih secara mandiri dari nol.{RESET}")  # Print sukses training model

    # Tampilkan struktur pohon keputusan yang terbentuk setelah training
    print("\n" + f"{MAGENTA}="*80 + f"{RESET}")  # Print garis batas atas pohon
    print(f"{BOLD}{YELLOW}{'{:^80}'.format('STRUKTUR POHON KEPUTUSAN YANG TERBENTUK (PROSES SELEKSI)')}{RESET}")  # Print nama panel pohon
    print(f"{MAGENTA}="*80 + f"{RESET}")  # Print pembatas tengah pohon
    print_decision_tree(clf.root, feature_names)    # Cetak struktur pohon secara rekursif
    print(f"{MAGENTA}="*80 + f"{RESET}")  # Print garis batas bawah pohon

    # Jalankan prediksi model pada data uji (X_test)
    y_pred  = clf.predict(X_test)                   # Dapatkan prediksi untuk semua data uji
    metrics = evaluate_performance(y_test, y_pred)  # Hitung semua metrik evaluasi

    # Tampilkan hasil evaluasi model
    print("\n" + f"{MAGENTA}+" + "="*78 + f"+{RESET}")  # Print border atas evaluasi
    print(f"{MAGENTA}|{RESET}{BOLD}{YELLOW}{'{:^78}'.format('HASIL EVALUASI MODEL')}{RESET}{MAGENTA}|{RESET}")  # Print judul evaluasi
    print(f"{MAGENTA}+" + "="*78 + f"+{RESET}")  # Print border tengah evaluasi
    print(f"{MAGENTA}|{RESET}  Accuracy   : {GREEN}{'{:<60.2f}'.format(metrics['accuracy']   * 100)}%{RESET} {MAGENTA}|{RESET}")  # Print akurasi
    print(f"{MAGENTA}|{RESET}  Precision  : {GREEN}{'{:<60.2f}'.format(metrics['precision']  * 100)}%{RESET} {MAGENTA}|{RESET}")  # Print presisi
    print(f"{MAGENTA}|{RESET}  Recall     : {GREEN}{'{:<60.2f}'.format(metrics['recall']     * 100)}%{RESET} {MAGENTA}|{RESET}")  # Print recall
    print(f"{MAGENTA}|{RESET}  F1-Score   : {GREEN}{'{:<60.2f}'.format(metrics['f1']         * 100)}%{RESET} {MAGENTA}|{RESET}")  # Print F1-score
    print(f"{MAGENTA}+" + "-"*78 + f"+{RESET}")  # Print pembatas tabel matrix

    # Tampilkan Confusion Matrix
    matrix = metrics['matrix']  # Dapatkan objek matrix confusion
    print(f"{MAGENTA}|{RESET}{BOLD}{CYAN}{'{:^78}'.format('Confusion Matrix')}{RESET}{MAGENTA}|{RESET}")  # Print header matrix
    print(f"{MAGENTA}+" + "-"*78 + f"+{RESET}")  # Print garis matrix
    print(f"{MAGENTA}|{RESET}                       Prediksi ORGANIK         Prediksi ANORGANIK          {MAGENTA}|{RESET}")  # Print label kolom prediksi
    print(f"{MAGENTA}|{RESET}  Aktual ORGANIK       {GREEN}{'{:<24}'.format(matrix['TP'])}{RESET} {RED}{'{:<27}'.format(matrix['FN'])}{RESET} {MAGENTA}|{RESET}")   # TP = Benar Organik | FN = Salah Anorganik
    print(f"{MAGENTA}|{RESET}  Aktual ANORGANIK     {RED}{'{:<24}'.format(matrix['FP'])}{RESET} {BLUE}{'{:<27}'.format(matrix['TN'])}{RESET} {MAGENTA}|{RESET}")   # FP = Salah Organik | TN = Benar Anorganik
    print(f"{MAGENTA}+" + "="*78 + f"+{RESET}")  # Print pembatas penutup evaluasi

    input(f"\n{YELLOW}Tekan ENTER untuk masuk ke Modul Interaktif...{RESET}")  # Print instruksi jeda ENTER

    tampilkan_daftar = True  # Flag penampil daftar gambar
    options = []  # List penyimpan item menu pilihan gambar

    # -----------------------------------------------------------------------
    # LOOP UTAMA MODUL INTERAKTIF
    # Program terus berjalan sampai user memilih keluar (X atau pilihan 2)
    # -----------------------------------------------------------------------
    while True:  # Mulai perulangan interaktif utama

        # Perbarui daftar gambar setiap iterasi loop (agar gambar baru langsung terdeteksi)
        organik_imgs   = sorted([f for f in os.listdir(dir_organik)   if f.lower().endswith(('.png', '.jpg', '.jpeg'))])  # Ambil file organik terbaru
        anorganik_imgs = sorted([f for f in os.listdir(dir_anorganik) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])  # Ambil file anorganik terbaru

        # Buat list options berisi tuple (path_lengkap, nama_file, label_folder) untuk setiap gambar
        options = []  # Reset list opsi
        for file in organik_imgs:  # Loop setiap file organik
            options.append((os.path.join(dir_organik, file), file, "Organik"))      # Gambar dari folder Organik
        for file in anorganik_imgs:  # Loop setiap file anorganik
            options.append((os.path.join(dir_anorganik, file), file, "Anorganik"))  # Gambar dari folder Anorganik

        # Tampilkan daftar gambar dan header menu jika dalam mode utama
        if tampilkan_daftar:  # Cek jika harus mencetak daftar
            os.system('cls' if os.name == 'nt' else 'clear')   # Bersihkan layar terminal
            print(f"{MAGENTA}={'='*78}={RESET}")  # Cetak pembatas menu atas
            print(f"{BOLD}{YELLOW}{'{:^80}'.format('MODUL INTERAKTIF KLASIFIKASI CITRA SAMPAH')}{RESET}")  # Cetak nama menu utama
            print(f"{MAGENTA}={'='*78}={RESET}")  # Cetak pembatas menu tengah
            print(f"\n{BOLD}Daftar file gambar terdeteksi dalam dataset:{RESET}")  # Cetak label sub-menu list

            # Tampilkan setiap gambar dengan nomor urut
            for idx, (path, name, label) in enumerate(options):  # Loop data list options
                print("  [{:02d}] {}".format(idx + 1, name))   # Format: [01] nama_file.png

        # Tampilkan instruksi input sesuai state
        if tampilkan_daftar:  # Jika status tampilkan_daftar aktif
            print(f"{MAGENTA}" + "-"*80 + f"{RESET}")  # Print garis menu bawah
            print(f"{BOLD}{CYAN}Masukkan nomor gambar (1-{len(options)}) untuk mengklasifikasikan.{RESET}")  # Tampilkan pesan pilih gambar
            print(f"  {BOLD}[X]{RESET} Keluar")  # Tampilkan pilihan keluar program
        else:  # Jika daftar disembunyikan
            print(f"{MAGENTA}" + "-"*80 + f"{RESET}")  # Print garis pemisah ringkas

        pilihan = input("Pilih nomor / opsi: ").strip()    # Baca input dari user, hapus spasi di ujung
        if not pilihan:     # Jika user hanya tekan Enter tanpa input, ulangi loop
            continue  # Mulai ulang loop input

        # -----------------------------------------------------------------------
        # OPSI X — Keluar dari program
        # -----------------------------------------------------------------------
        if pilihan.upper() == 'X':  # Jika user memilih keluar (X)
            print("\n" + f"{MAGENTA}+" + "="*78 + f"+{RESET}")  # Print pembatas atas pesan penutup
            print(f"{MAGENTA}|{RESET}{BOLD}{GREEN}{'{:^78}'.format('Terima kasih! Tetap semangat menjaga kelestarian lingkungan hidup.')}{RESET}{MAGENTA}|{RESET}")  # Print pesan sukses keluar
            print(f"{MAGENTA}+" + "="*78 + f"+{RESET}")  # Print pembatas bawah pesan penutup
            try:  # Tangani exception menutup window
                cv2.destroyAllWindows()     # Tutup semua jendela OpenCV yang mungkin masih terbuka
            except Exception:  # Abaikan jika terjadi error window
                pass  # Lanjutkan proses exit
            break   # Keluar dari while loop → program selesai

        # -----------------------------------------------------------------------
        # OPSI M — Kembali ke tampilan daftar gambar (menu utama)
        # -----------------------------------------------------------------------
        if pilihan.upper() == 'M':  # Jika memilih menu utama (M)
            tampilkan_daftar = True  # Aktifkan flag tampilkan_daftar
            continue  # Mulai kembali loop utama dari menu list


        # -----------------------------------------------------------------------
        # OPSI ANGKA / A — Pilih gambar dari daftar (single, range, atau semua)
        # -----------------------------------------------------------------------
        valid_indices = []  # List indeks gambar yang dipilih user (0-indexed)

        if pilihan.upper() == 'A':      # 'A' = pilih semua gambar sekaligus
            valid_indices = list(range(len(options)))  # Gunakan semua indeks yang terdeteksi

        else:   # Proses input angka: bisa tunggal (misal: "3"), pisah koma (misal: "1,3,5"), atau range (misal: "2-5")
            chosen_numbers = []  # List sementara penyimpan nomor terpilih
            parts = pilihan.split(",")  # Pisah input berdasarkan koma untuk multi-pilih

            for part in parts:  # Iterasi setiap potongan input
                part = part.strip()     # Hapus spasi di setiap bagian
                if not part:  # Cek jika elemen pemisah kosong
                    continue            # Lewati bagian kosong

                if "-" in part:         # Jika mengandung "-", coba parse sebagai rentang (range)
                    subparts = part.split("-")  # Pisah dengan tanda hubung range
                    if len(subparts) == 2 and subparts[0].strip().isdigit() and subparts[1].strip().isdigit():  # Cek validitas angka range
                        start = int(subparts[0].strip())    # Nomor awal range
                        end   = int(subparts[1].strip())    # Nomor akhir range
                        if start <= end:  # Jika rentang bernilai naik
                            chosen_numbers.extend(range(start, end + 1))        # Range naik
                        else:  # Jika rentang bernilai turun
                            chosen_numbers.extend(range(start, end - 1, -1))    # Range turun
                    else:  # Jika format range salah
                        print(f"{RED}[WARN] Format rentang '{part}' tidak valid!{RESET}")  # Format range salah
                elif part.isdigit():            # Jika angka tunggal
                    chosen_numbers.append(int(part))  # Simpan nomor terpilih tunggal
                else:  # Jika format tidak dikenali
                    print(f"{RED}[WARN] Format '{part}' tidak dikenali!{RESET}")   # Input tidak dikenal

            # Validasi setiap nomor yang dipilih: harus dalam rentang 1 s.d. jumlah gambar
            for num in chosen_numbers:  # Loop seluruh nomor pilihan user
                if 1 <= num <= len(options):  # Cek batas minimal dan maksimal nomor
                    valid_indices.append(num - 1)   # Konversi ke 0-indexed
                else:  # Jika di luar rentang daftar gambar
                    print(f"{RED}[WARN] Nomor gambar [{num:02d}] di luar jangkauan (1-{len(options)})!{RESET}")  # Peringatan jangkauan salah

        # Jika tidak ada gambar valid yang dipilih, minta user mencoba lagi
        if not valid_indices:  # Jika list indeks kosong
            print(f"{RED}[WARN] Tidak ada gambar valid yang dipilih. Silakan coba lagi.{RESET}")  # Print info tidak ada pilihan
            continue  # Lanjutkan perulangan input berikutnya

        # -----------------------------------------------------------------------
        # PROSES KLASIFIKASI UNTUK SEMUA GAMBAR YANG DIPILIH
        # -----------------------------------------------------------------------
        for rank, idx in enumerate(valid_indices):  # Perulangan memproses setiap gambar pilihan
            selected_path, name, label = options[idx]   # Ambil info gambar: path, nama, dan label folder

            # Cetak header pemrosesan gambar ini
            print(f"\n{BOLD}{MAGENTA}" + "-"*80 + f"{RESET}")  # Print pembatas atas proses
            print(f"{BOLD}{YELLOW}  MEMPROSES CITRA [{rank+1}/{len(valid_indices)}]: {name}{RESET}")  # Print info berkas yang diproses
            print(f"{BOLD}{MAGENTA}" + "-"*80 + f"{RESET}")  # Print pembatas bawah proses

            test_img = cv2.imread(selected_path)    # Baca gambar dari path
            if test_img is None:                    # Lewati jika gagal dibaca
                print(f"{RED}[ERR] File '{name}' gagal dibaca!{RESET}")  # Print log error baca berkas
                continue  # Lewati dan proses berkas berikutnya

            # Coba tampilkan gambar di jendela GUI
            try:  # Jalankan GUI window OpenCV
                cv2.destroyAllWindows()                                     # Tutup jendela sebelumnya
                cv2.namedWindow("Citra Sampah Uji", cv2.WINDOW_NORMAL)     # Buat jendela baru
                cv2.imshow("Citra Sampah Uji", test_img)                   # Tampilkan gambar
                cv2.waitKey(1)                                              # Proses event agar jendela tampil
                print(f"[GUI] Menampilkan jendela '{name}'...")  # Print log GUI sukses
            except Exception:  # Jika headless server
                print("[INFO] Menjalankan sistem headless (tanpa GUI).")    # Fallback jika tidak ada GUI

            # Ubah ukuran gambar dan ekstraksi fitur RGB
            img_resized = cv2.resize(test_img, (64, 64))    # Samakan ukuran ke 64x64 piksel
            tb = np.mean(img_resized[:, :, 0])              # Rata-rata Blue
            tg = np.mean(img_resized[:, :, 1])              # Rata-rata Green
            tr = np.mean(img_resized[:, :, 2])              # Rata-rata Red

            fitur_uji = [tr, tg, tb]    # Susun vektor fitur [R, G, B]

            # Klasifikasi gambar dan dapatkan jalur keputusan
            kategori_prediksi, path_steps = clf.predict_with_path(fitur_uji, feature_names)  # Jalankan model prediksi

            # Tampilkan nilai fitur dan jalur keputusan pohon
            print(f"\n{CYAN}>>> Rerata RGB yang Diekstrak:{RESET} R={tr:.2f}, G={tg:.2f}, B={tb:.2f}")  # Print nilai RGB
            print(f"{YELLOW}>>> Alur Keputusan Decision Tree:{RESET}")  # Print header rute

            for step_idx, step in enumerate(path_steps):   # Tampilkan setiap langkah keputusan
                if "=> [TRUE]" in step:  # Jika bernilai True
                    formatted_step = step.replace("=> [TRUE]",  f"=> {GREEN}TRUE (Belok Kiri){RESET}")  # Format warna True
                else:  # Jika bernilai False
                    formatted_step = step.replace("=> [FALSE]", f"=> {RED}FALSE (Belok Kanan){RESET}")  # Format warna False
                print(f"    Langkah {step_idx+1}: {formatted_step}")  # Print log rute keputusan

            # Tampilkan kotak hasil klasifikasi dan rekomendasi pengelolaan
            color_pred = GREEN if kategori_prediksi == "Organik" else BLUE  # Tentukan warna teks hasil
            print(f"\n{color_pred}+" + "-"*68 + f"+{RESET}")  # Print pembatas atas box hasil
            print(f"{color_pred}|{RESET}{BOLD}{'{:^68}'.format('HASIL KLASIFIKASI CITRA SAMPAH')}{RESET}{color_pred}|{RESET}")  # Print judul box hasil
            print(f"{color_pred}+" + "-"*68 + f"+{RESET}")  # Print pembatas tengah box hasil
            print(f"{color_pred}|{RESET}  Nama File    : {BOLD}{'{:<48}'.format(name)}{RESET} {color_pred}|{RESET}")  # Print nama berkas
            print(f"{color_pred}|{RESET}  Kategori     : {BOLD}{color_pred}{'{:<48}'.format(kategori_prediksi.upper())}{RESET} {color_pred}|{RESET}")  # Print hasil prediksi kategori
            print(f"{color_pred}+" + "-"*68 + f"+{RESET}")  # Print pembatas bawah kategori
            print(f"{color_pred}|{RESET}{BOLD}{'{:^68}'.format('REKOMENDASI PENGELOLAAN YANG DISARANKAN')}{RESET}{color_pred}|{RESET}")  # Print judul box rekomendasi
            print(f"{color_pred}+" + "-"*68 + f"+{RESET}")  # Print pembatas tengah rekomendasi

            if kategori_prediksi == "Organik":  # Cek jika berlabel Organik
                print(f"{color_pred}|{RESET}  - Lakukan pengomposan (Composting) untuk pupuk tanaman            {color_pred}|{RESET}")  # Rekomendasi kompos
                print(f"{color_pred}|{RESET}  - Gunakan sebagai media pakan budidaya maggot BSF (Black Soldier)   {color_pred}|{RESET}")  # Rekomendasi maggot
                print(f"{color_pred}|{RESET}  - Olah menjadi cairan Eco-Enzyme serbaguna alami                   {color_pred}|{RESET}")  # Rekomendasi eco-enzyme
            else:  # Cek jika berlabel Anorganik
                print(f"{color_pred}|{RESET}  - Pisahkan sesuai bahan (Plastik, Logam, Kertas, Kaca)             {color_pred}|{RESET}")  # Rekomendasi pilah sampah
                print(f"{color_pred}|{RESET}  - Setorkan ke Bank Sampah terdekat agar didaur ulang               {color_pred}|{RESET}")  # Rekomendasi bank sampah
                print(f"{color_pred}|{RESET}  - Hindari membakar plastik demi kesehatan pernapasan               {color_pred}|{RESET}")  # Rekomendasi cegah pembakaran
            print(f"{color_pred}+" + "-"*68 + f"+{RESET}")  # Print pembatas penutup box

            # Jika batch mode dan masih ada gambar berikutnya, beri jeda sebelum lanjut
            if len(valid_indices) > 1 and rank < len(valid_indices) - 1:  # Cek jika ada item berikutnya dalam batch
                input(f"\n{YELLOW}Tekan ENTER untuk memproses gambar berikutnya [{rank+2}/{len(valid_indices)}]...{RESET}")  # Tampilkan instruksi jeda ENTER

        # -----------------------------------------------------------------------
        # Setelah semua gambar selesai diproses, tampilkan pilihan lanjutan
        # -----------------------------------------------------------------------
        print(f"\n{BOLD}  [1]{RESET} Lanjut pilih gambar lain")   # Opsi kembali ke daftar gambar
        print(f"  {BOLD}[2]{RESET} Stop & Keluar program")         # Opsi keluar program
        print(f"{MAGENTA}" + "-"*80 + f"{RESET}")  # Print garis pembatas panel penutup

        # Loop kecil untuk memastikan user memasukkan pilihan yang valid (1 atau 2)
        while True:  # Loop validasi input opsi kelanjutan
            lanjut = input("Pilihan (1/2): ").strip()   # Baca pilihan user

            if lanjut == "1":           # User ingin memilih gambar lain
                tampilkan_daftar = True # Kembali ke mode daftar gambar
                break                   # Keluar dari loop kecil, lanjutkan loop utama

            elif lanjut == "2":         # User ingin keluar dari program
                print("\n" + f"{MAGENTA}+" + "="*78 + f"+{RESET}")  # Print border atas penutup
                print(f"{MAGENTA}|{RESET}{BOLD}{GREEN}{'{:^78}'.format('Terima kasih! Tetap semangat menjaga kelestarian lingkungan hidup.')}{RESET}{MAGENTA}|{RESET}")  # Print pesan sukses keluar
                print(f"{MAGENTA}+" + "="*78 + f"+{RESET}")  # Print border bawah penutup
                try:  # Tangani exception menutup window OpenCV
                    cv2.destroyAllWindows()     # Tutup semua jendela OpenCV
                except Exception:  # Abaikan error window jika ada
                    pass  # Lanjutkan proses exit
                import sys          # Import sys untuk memanggil sys.exit()
                sys.exit(0)         # Keluar dari program dengan kode sukses (0)

            else:   # Input tidak valid
                print(f"{RED}[WARN] Masukkan 1 untuk lanjut atau 2 untuk stop.{RESET}")  # Print peringatan input salah
