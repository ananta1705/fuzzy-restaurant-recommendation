# ==============================================================================
# KLASIFIKASI GAMBAR SAMPAH ORGANIK DAN ANORGANIK
# Metode: Decision Tree From Scratch (Tanpa Library ML)
# Kelompok 5 - Tugas Besar Kecerdasan Buatan
# ==============================================================================

import os
import cv2
import numpy as np
import random
import sys

# Aktifkan warna ANSI di terminal Windows
if sys.platform.startswith('win'):
    os.system('color')

# Kode warna ANSI
GREEN     = "\033[1;32m"
BLUE      = "\033[1;34m"
YELLOW    = "\033[1;33m"
RED       = "\033[1;31m"
CYAN      = "\033[1;36m"
MAGENTA   = "\033[1;35m"
RESET     = "\033[0m"
BOLD      = "\033[1m"
UNDERLINE = "\033[4m"






# ==============================================================================
# BAGIAN 1: IMPLEMENTASI DECISION TREE DARI NOL (TANPA LIBRARY ML)
# ==============================================================================

class Node:
    """Satu simpul dalam pohon keputusan"""
    def __init__(self, feature_idx=None, threshold=None, left=None, right=None, value=None):
        self.feature_idx = feature_idx  # Indeks fitur (0=R, 1=G, 2=B)
        self.threshold   = threshold    # Nilai batas pemisah
        self.left        = left         # Cabang kiri (nilai <= threshold)
        self.right       = right        # Cabang kanan (nilai > threshold)
        self.value       = value        # Kelas hasil (hanya pada node daun)

    def is_leaf(self):
        return self.value is not None


# Hitung nilai Gini Impurity
def calculate_gini(labels):
    if not labels:
        return 0

    total = len(labels)
    counts = {}
    for label in labels:
        counts[label] = counts.get(label, 0) + 1

    gini = 1.0 - sum((count / total) ** 2 for count in counts.values())
    return gini


class DecisionTreeClassifierScratch:
    """Decision Tree Classifier dari nol, menggunakan Gini Impurity"""
    def __init__(self, max_depth=5, min_samples_split=2):
        self.max_depth         = max_depth
        self.min_samples_split = min_samples_split
        self.root              = None

    def fit(self, X, y):
        """Bangun pohon dari data latih"""
        self.root = self._build_tree(X, y, depth=0)

    def _build_tree(self, X, y, depth):
        """Rekursif: bangun pohon hingga kondisi berhenti terpenuhi"""
        num_samples    = len(X)
        if num_samples == 0:
            return None

        num_features   = len(X[0])
        unique_classes = set(y)

        # Kondisi berhenti: max depth, node murni, atau sampel terlalu sedikit
        if (depth >= self.max_depth or
            len(unique_classes) == 1 or
            num_samples < self.min_samples_split):
            leaf_value = max(unique_classes, key=y.count)
            return Node(value=leaf_value)

        # Cari split terbaik berdasarkan Gini terendah
        best_idx, best_thresh = self._best_split(X, y, num_features)

        if best_idx is None:
            leaf_value = max(unique_classes, key=y.count)
            return Node(value=leaf_value)

        left_X, left_y, right_X, right_y = self._split(X, y, best_idx, best_thresh)

        if not left_X or not right_X:
            leaf_value = max(unique_classes, key=y.count)
            return Node(value=leaf_value)

        left_child  = self._build_tree(left_X,  left_y,  depth + 1)
        right_child = self._build_tree(right_X, right_y, depth + 1)

        return Node(feature_idx=best_idx, threshold=best_thresh, left=left_child, right=right_child)

    def _best_split(self, X, y, num_features):
        """Cari fitur + threshold dengan Gini Impurity terkecil"""
        best_gini   = 999.0
        best_idx    = None
        best_thresh = None

        for idx in range(num_features):
            values = sorted(list(set(sample[idx] for sample in X)))

            # Kandidat threshold: titik tengah antar nilai berurutan
            thresholds = []
            for i in range(len(values) - 1):
                thresholds.append((values[i] + values[i+1]) / 2.0)

            if not thresholds and values:
                thresholds = [values[0]]

            for thresh in thresholds:
                left_X, left_y, right_X, right_y = self._split(X, y, idx, thresh)

                if not left_y or not right_y:
                    continue

                # Hitung Weighted Gini
                p_left     = len(left_y) / len(y)
                p_right    = len(right_y) / len(y)
                gini_split = (p_left * calculate_gini(left_y)) + (p_right * calculate_gini(right_y))

                if gini_split < best_gini:
                    best_gini   = gini_split
                    best_idx    = idx
                    best_thresh = thresh

        return best_idx, best_thresh

    def _split(self, X, y, feature_idx, threshold):
        """Pisah data ke cabang kiri (<= threshold) dan kanan (> threshold)"""
        left_X, left_y, right_X, right_y = [], [], [], []

        for sample, label in zip(X, y):
            if sample[feature_idx] <= threshold:
                left_X.append(sample)
                left_y.append(label)
            else:
                right_X.append(sample)
                right_y.append(label)

        return left_X, left_y, right_X, right_y

    def predict(self, X):
        """Prediksi kelas untuk sekumpulan sampel"""
        return [self._traverse(sample, self.root) for sample in X]

    def _traverse(self, sample, node):
        """Susuri pohon dari akar hingga daun untuk satu sampel"""
        if node.is_leaf():
            return node.value

        if sample[node.feature_idx] <= node.threshold:
            return self._traverse(sample, node.left)
        else:
            return self._traverse(sample, node.right)

    def predict_with_path(self, sample, feature_names):
        """Prediksi kelas dan catat jalur keputusan pohon"""
        path_steps = []
        node = self.root

        while not node.is_leaf():
            feat_name = feature_names[node.feature_idx]
            val       = sample[node.feature_idx]

            if val <= node.threshold:
                path_steps.append(f"Apakah {feat_name} <= {node.threshold:.2f}? (Nilai: {val:.2f}) => [TRUE]")
                node = node.left
            else:
                path_steps.append(f"Apakah {feat_name} <= {node.threshold:.2f}? (Nilai: {val:.2f}) => [FALSE]")
                node = node.right

        return node.value, path_steps


# ==============================================================================
# BAGIAN 2: TRAIN/TEST SPLIT & EVALUASI MODEL
# ==============================================================================

# Bagi dataset menjadi data latih dan data uji
def train_test_split_scratch(X, y, test_size=0.2, seed=42):
    random.seed(seed)
    combined = list(zip(X, y))
    random.shuffle(combined)

    split_idx = int(len(combined) * (1 - test_size))

    X_train, y_train = zip(*combined[:split_idx])   # 80% latih
    X_test,  y_test  = zip(*combined[split_idx:])   # 20% uji

    return list(X_train), list(X_test), list(y_train), list(y_test)


# Hitung metrik evaluasi: Accuracy, Precision, Recall, F1, Confusion Matrix
def evaluate_performance(y_true, y_pred):
    total    = len(y_true)
    accuracy = sum(1 for t, p in zip(y_true, y_pred) if t == p) / total

    # Confusion Matrix (Organik = kelas Positif)
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == "Organik"   and p == "Organik")
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == "Anorganik" and p == "Organik")
    tn = sum(1 for t, p in zip(y_true, y_pred) if t == "Anorganik" and p == "Anorganik")
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == "Organik"   and p == "Anorganik")

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1        = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return {
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
def print_decision_tree(node, feature_names, depth=0, prefix="Root"):
    if node is None:
        return

    indent = "    " * depth

    if node.is_leaf():
        color = GREEN if node.value == "Organik" else BLUE
        print(f"{indent}\\-- {YELLOW}[Daun]{RESET} {prefix} => {BOLD}HASIL: {color}{node.value}{RESET}")
        return

    feat_name = feature_names[node.feature_idx]
    print(f"{indent}|-- {CYAN}[Cabang]{RESET} {prefix} => JIKA {BOLD}{feat_name} <= {node.threshold:.2f}{RESET}")

    print_decision_tree(node.left,  feature_names, depth + 1, f"{GREEN}Kiri (True){RESET}")
    print_decision_tree(node.right, feature_names, depth + 1, f"{RED}Kanan (False){RESET}")


# ==============================================================================
# BAGIAN 4: ALUR UTAMA PROGRAM
# ==============================================================================
if __name__ == "__main__":

    # Header program
    print("=" * 60)
    print("TUGAS BESAR KECERDASAN BUATAN")
    print("Klasifikasi Sampah Organik dan Anorganik")
    print("Metode : Decision Tree")
    print("=" * 60)
    print("Kelompok 5")
    print("Ananta Puti Maharani")
    print("Marta Safitri")
    print("=" * 60)

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
    # Ambil gambar organik
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
    # Ambil gambar anorganik
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

    # Tampilkan informasi dataset
    print(f"\n{CYAN}" + "-"*60 + f"{RESET}")
    print(f" {BOLD}INFORMASI DATASET:{RESET}")
    print(f"  Total Data  : {BOLD}{len(X)}{RESET} sampel")
    print(f"  Organik     : {GREEN}{y.count('Organik')}{RESET} sampel")
    print(f"  Anorganik   : {BLUE}{y.count('Anorganik')}{RESET} sampel")
    print(f"{CYAN}" + "-"*60 + f"{RESET}")

    # Tampilkan 5 sampel pertama
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

    # Tampilkan hasil evaluasi model
    print("\n" + f"{MAGENTA}+" + "="*78 + f"+{RESET}")
    print(f"{MAGENTA}|{RESET}{BOLD}{YELLOW}{'{:^78}'.format('HASIL EVALUASI MODEL')}{RESET}{MAGENTA}|{RESET}")
    print(f"{MAGENTA}+" + "="*78 + f"+{RESET}")
    print(f"{MAGENTA}|{RESET}  Accuracy   : {GREEN}{'{:<60.2f}'.format(metrics['accuracy']   * 100)}%{RESET} {MAGENTA}|{RESET}")
    print(f"{MAGENTA}|{RESET}  Precision  : {GREEN}{'{:<60.2f}'.format(metrics['precision']  * 100)}%{RESET} {MAGENTA}|{RESET}")
    print(f"{MAGENTA}|{RESET}  Recall     : {GREEN}{'{:<60.2f}'.format(metrics['recall']     * 100)}%{RESET} {MAGENTA}|{RESET}")
    print(f"{MAGENTA}|{RESET}  F1-Score   : {GREEN}{'{:<60.2f}'.format(metrics['f1']         * 100)}%{RESET} {MAGENTA}|{RESET}")
    print(f"{MAGENTA}+" + "-"*78 + f"+{RESET}")

    # Tampilkan Confusion Matrix
    matrix = metrics['matrix']
    print(f"{MAGENTA}|{RESET}{BOLD}{CYAN}{'{:^78}'.format('Confusion Matrix')}{RESET}{MAGENTA}|{RESET}")
    print(f"{MAGENTA}+" + "-"*78 + f"+{RESET}")
    print(f"{MAGENTA}|{RESET}                       Prediksi ORGANIK         Prediksi ANORGANIK          {MAGENTA}|{RESET}")
    print(f"{MAGENTA}|{RESET}  Aktual ORGANIK       {GREEN}{'{:<24}'.format(matrix['TP'])}{RESET} {RED}{'{:<27}'.format(matrix['FN'])}{RESET} {MAGENTA}|{RESET}")   # TP = Benar Organik | FN = Salah Anorganik
    print(f"{MAGENTA}|{RESET}  Aktual ANORGANIK     {RED}{'{:<24}'.format(matrix['FP'])}{RESET} {BLUE}{'{:<27}'.format(matrix['TN'])}{RESET} {MAGENTA}|{RESET}")   # FP = Salah Organik | TN = Benar Anorganik
    print(f"{MAGENTA}+" + "="*78 + f"+{RESET}")

    input(f"\n{YELLOW}Tekan ENTER untuk masuk ke Modul Interaktif...{RESET}")

    tampilkan_daftar = True
    options = []

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
            print(f"{BOLD}{CYAN}Masukkan nomor gambar (1-{len(options)}) untuk mengklasifikasikan.{RESET}")
            print(f"  {BOLD}[C]{RESET} Gambar kustom (input path sendiri)")
            print(f"  {BOLD}[X]{RESET} Keluar")
        else:
            print(f"{MAGENTA}" + "-"*80 + f"{RESET}")

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
            tampilkan_daftar = True
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
