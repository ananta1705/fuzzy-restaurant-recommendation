# ==============================================================================
# KLASIFIKASI GAMBAR SAMPAH ORGANIK DAN ANORGANIK DENGAN DECISION TREE CUSTOM (NO-ML-LIB)
# Untuk Mendukung Pengelolaan Lingkungan Hidup Berkelanjutan
# ==============================================================================

import os
import cv2
import numpy as np
import random
import sys

# Kode warna ANSI untuk antarmuka terminal yang menarik dan interaktif
if sys.platform.startswith('win'):
    import os
    os.system('color')  # Menginisialisasi konsol Windows agar mendukung kode warna ANSI

GREEN = "\033[1;32m"
BLUE = "\033[1;34m"
YELLOW = "\033[1;33m"
RED = "\033[1;31m"
CYAN = "\033[1;36m"
MAGENTA = "\033[1;35m"
RESET = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"

def tampilkan_cara_kerja():
    """Menampilkan presentasi slide-by-slide mengenai cara kerja dan matematika Decision Tree"""
    slides = [
        # Slide 1: Pengantar
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

        # Slide 2: Ekstraksi Fitur Warna
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

        # Slide 3: Gini Impurity
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

        # Slide 4: Pemilihan Split Terbaik
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

        # Slide 5: Visualisasi Alur Klasifikasi
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

    for slide in slides:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(slide)
        input()

# ------------------------------------------------------------------------------
# 1. PEMBUATAN DATASET GAMBAR DEMO (DUMMY IMAGE GENERATION)
# ------------------------------------------------------------------------------
def generate_dummy_images(dir_organik, dir_anorganik, num_images=15):
    """
    Membuat file gambar dummy (.png) jika folder dataset memiliki jumlah gambar kurang dari num_images.
    - Sampah Organik: Gambar berwarna dominan Hijau / Cokelat
    - Sampah Anorganik: Gambar berwarna dominan Biru / Merah / Abu-abu
    """
    random.seed(42)
    
    # Cek dan buat gambar untuk Organik
    existing_organik = [f for f in os.listdir(dir_organik) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if len(existing_organik) < num_images:
        needed = num_images - len(existing_organik)
        print(f"Folder Organik memiliki {len(existing_organik)} gambar. Menambahkan {needed} gambar dummy organik...")
        for i in range(needed):
            img = np.zeros((64, 64, 3), dtype=np.uint8)
            # Tentukan warna dasar hijau-cokelat
            base_g = random.randint(120, 220)
            base_r = random.randint(60, 140)
            base_b = random.randint(20, 60)
            
            # Isi piksel secara acak tipis agar gambar terlihat alami
            for r in range(64):
                for c in range(64):
                    img[r, c, 0] = max(0, min(255, base_b + random.randint(-15, 15))) # B
                    img[r, c, 1] = max(0, min(255, base_g + random.randint(-15, 15))) # G
                    img[r, c, 2] = max(0, min(255, base_r + random.randint(-15, 15))) # R
            
            filename = f"dummy_organik_{i+1}.png"
            cv2.imwrite(os.path.join(dir_organik, filename), img)
            
    # Cek dan buat gambar untuk Anorganik
    existing_anorganik = [f for f in os.listdir(dir_anorganik) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if len(existing_anorganik) < num_images:
        needed = num_images - len(existing_anorganik)
        print(f"Folder Anorganik memiliki {len(existing_anorganik)} gambar. Menambahkan {needed} gambar dummy anorganik...")
        for i in range(needed):
            img = np.zeros((64, 64, 3), dtype=np.uint8)
            
            # Acak kategori warna anorganik
            tipe = random.choice(["biru", "merah", "abu"])
            if tipe == "biru":
                base_b, base_g, base_r = random.randint(150, 240), random.randint(30, 100), random.randint(30, 100)
            elif tipe == "merah":
                base_b, base_g, base_r = random.randint(30, 80), random.randint(30, 80), random.randint(150, 240)
            else: # abu-abu
                val = random.randint(100, 180)
                base_b, base_g, base_r = val, val, val
                
            for r in range(64):
                for c in range(64):
                    img[r, c, 0] = max(0, min(255, base_b + random.randint(-15, 15))) # B
                    img[r, c, 1] = max(0, min(255, base_g + random.randint(-15, 15))) # G
                    img[r, c, 2] = max(0, min(255, base_r + random.randint(-15, 15))) # R
            
            filename = f"dummy_anorganik_{i+1}.png"
            cv2.imwrite(os.path.join(dir_anorganik, filename), img)


# ------------------------------------------------------------------------------
# 2. ALGORITMA DECISION TREE DARI NOL (DECISION TREE CLASSIFIER SCRATCH)
# ------------------------------------------------------------------------------
class Node:
    def __init__(self, feature_idx=None, threshold=None, left=None, right=None, value=None):
        self.feature_idx = feature_idx  # Indeks fitur pemisah (0=R, 1=G, 2=B)
        self.threshold = threshold      # Nilai batas pemisah
        self.left = left                # Cabang kiri
        self.right = right              # Cabang kanan
        self.value = value              # Kategori kelas (jika daun)

    def is_leaf(self):
        return self.value is not None


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
    def __init__(self, max_depth=5, min_samples_split=2):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.root = None

    def fit(self, X, y):
        self.root = self._build_tree(X, y, depth=0)

    def _build_tree(self, X, y, depth):
        num_samples = len(X)
        if num_samples == 0:
            return None

        num_features = len(X[0])
        unique_classes = set(y)

        # Hentikan rekursi jika mencapai batas kedalaman, kelas homogen, atau jumlah sampel terlalu sedikit
        if (depth >= self.max_depth or 
            len(unique_classes) == 1 or 
            num_samples < self.min_samples_split):
            leaf_value = max(unique_classes, key=y.count)
            return Node(value=leaf_value)

        best_idx, best_thresh = self._best_split(X, y, num_features)
        if best_idx is None:
            leaf_value = max(unique_classes, key=y.count)
            return Node(value=leaf_value)

        left_X, left_y, right_X, right_y = self._split(X, y, best_idx, best_thresh)
        if not left_X or not right_X:
            leaf_value = max(unique_classes, key=y.count)
            return Node(value=leaf_value)

        left_child = self._build_tree(left_X, left_y, depth + 1)
        right_child = self._build_tree(right_X, right_y, depth + 1)

        return Node(feature_idx=best_idx, threshold=best_thresh, left=left_child, right=right_child)

    def _best_split(self, X, y, num_features):
        best_gini = 999.0
        best_idx = None
        best_thresh = None

        for idx in range(num_features):
            values = sorted(list(set(sample[idx] for sample in X)))
            thresholds = []
            for i in range(len(values) - 1):
                thresholds.append((values[i] + values[i+1]) / 2.0)
            
            if not thresholds and values:
                thresholds = [values[0]]

            for thresh in thresholds:
                left_X, left_y, right_X, right_y = self._split(X, y, idx, thresh)
                if not left_y or not right_y:
                    continue

                p_left = len(left_y) / len(y)
                p_right = len(right_y) / len(y)
                gini_split = p_left * calculate_gini(left_y) + p_right * calculate_gini(right_y)

                if gini_split < best_gini:
                    best_gini = gini_split
                    best_idx = idx
                    best_thresh = thresh

        return best_idx, best_thresh

    def _split(self, X, y, feature_idx, threshold):
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
        return [self._traverse(sample, self.root) for sample in X]

    def _traverse(self, sample, node):
        if node.is_leaf():
            return node.value
        if sample[node.feature_idx] <= node.threshold:
            return self._traverse(sample, node.left)
        else:
            return self._traverse(sample, node.right)

    def predict_with_path(self, sample, feature_names):
        """Memprediksi kelas sampel tunggal dan mencatat alur keputusan pohon"""
        path_steps = []
        node = self.root
        while not node.is_leaf():
            feat_name = feature_names[node.feature_idx]
            val = sample[node.feature_idx]
            if val <= node.threshold:
                path_steps.append(f"Apakah {feat_name} <= {node.threshold:.2f}? (Nilai: {val:.2f}) => [TRUE]")
                node = node.left
            else:
                path_steps.append(f"Apakah {feat_name} <= {node.threshold:.2f}? (Nilai: {val:.2f}) => [FALSE]")
                node = node.right
        return node.value, path_steps


# ------------------------------------------------------------------------------
# 3. METODE PEMBAGIAN DATA & EVALUASI
# ------------------------------------------------------------------------------
def train_test_split_scratch(X, y, test_size=0.2, seed=42):
    random.seed(seed)
    combined = list(zip(X, y))
    random.shuffle(combined)
    split_idx = int(len(combined) * (1 - test_size))
    
    X_train, y_train = zip(*combined[:split_idx])
    X_test, y_test = zip(*combined[split_idx:])
    
    return list(X_train), list(X_test), list(y_train), list(y_test)


def evaluate_performance(y_true, y_pred):
    total = len(y_true)
    accuracy = sum(1 for t, p in zip(y_true, y_pred) if t == p) / total
    
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == "Organik" and p == "Organik")
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == "Anorganik" and p == "Organik")
    tn = sum(1 for t, p in zip(y_true, y_pred) if t == "Anorganik" and p == "Anorganik")
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == "Organik" and p == "Anorganik")
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "matrix": {"TP": tp, "FP": fp, "TN": tn, "FN": fn}
    }


# ------------------------------------------------------------------------------
# 4. VISUALISASI POHON KEPUTUSAN
# ------------------------------------------------------------------------------
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
    print_decision_tree(node.left, feature_names, depth + 1, f"{GREEN}Kiri (True){RESET}")
    print_decision_tree(node.right, feature_names, depth + 1, f"{RED}Kanan (False){RESET}")


# ------------------------------------------------------------------------------
# 5. ALUR UTAMA (MAIN APP FLOW)
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"{MAGENTA}+" + "="*78 + f"+{RESET}")
    print(f"{MAGENTA}|{RESET}{BOLD}{YELLOW}{'{:^78}'.format('TUGAS BESAR KECERDASAN BUATAN - DETEKSI SAMPAH MANDIRI')}{RESET}{MAGENTA}|{RESET}")
    print(f"{MAGENTA}|{RESET}{BOLD}{CYAN}{'{:^78}'.format('Sistem Klasifikasi Sampah Berbasis Citra - Decision Tree Custom')}{RESET}{MAGENTA}|{RESET}")
    print(f"{MAGENTA}|{RESET}{'{:^78}'.format('Mendukung Program Pengelolaan Lingkungan Berkelanjutan')}{RESET}{MAGENTA}|{RESET}")
    print(f"{MAGENTA}+" + "="*78 + f"+{RESET}")

    # Definisikan folder path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dir_organik = os.path.join(base_dir, "dataset", "Organik")
    dir_anorganik = os.path.join(base_dir, "dataset", "Anorganik")

    # Buat folder jika belum ada
    os.makedirs(dir_organik, exist_ok=True)
    os.makedirs(dir_anorganik, exist_ok=True)

    # Nama Fitur
    feature_names = [
        "Rerata Warna Merah (Red Mean)",
        "Rerata Warna Hijau (Green Mean)",
        "Rerata Warna Biru (Blue Mean)"
    ]

    # Ekstraksi Fitur dari File Gambar
    X = []
    y = []

    print(f"\n{CYAN}>>> Membaca file gambar dan mengekstraksi fitur warna RGB...{RESET}")

    # Membaca gambar Organik
    files_organik = [f for f in os.listdir(dir_organik) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    for file in files_organik:
        img_path = os.path.join(dir_organik, file)
        img = cv2.imread(img_path)
        if img is None:
            continue
        img = cv2.resize(img, (64, 64))

        # Ekstraksi fitur rata-rata warna RGB (OpenCV menggunakan format BGR)
        mean_b = np.mean(img[:, :, 0])
        mean_g = np.mean(img[:, :, 1])
        mean_r = np.mean(img[:, :, 2])

        X.append([mean_r, mean_g, mean_b])
        y.append("Organik")

    # Membaca gambar Anorganik
    files_anorganik = [f for f in os.listdir(dir_anorganik) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    for file in files_anorganik:
        img_path = os.path.join(dir_anorganik, file)
        img = cv2.imread(img_path)
        if img is None:
            continue
        img = cv2.resize(img, (64, 64))

        mean_b = np.mean(img[:, :, 0])
        mean_g = np.mean(img[:, :, 1])
        mean_r = np.mean(img[:, :, 2])

        X.append([mean_r, mean_g, mean_b])
        y.append("Anorganik")

    # Validasi jika tidak ada gambar terbaca
    if len(X) == 0:
        print(f"\n{RED}[ERR] Error: Tidak ada gambar yang berhasil dibaca dari dataset!{RESET}")
        sys.exit(1)

    print(f"\n{CYAN}" + "-"*80 + f"{RESET}")
    print(f" {BOLD}INFORMASI DATASET:{RESET}")
    print(f"  > Total gambar terproses : {BOLD}{len(X)}{RESET} sampel")
    print(f"  > Sampah Organik         : {GREEN}{y.count('Organik')}{RESET} sampel")
    print(f"  > Sampah Anorganik       : {BLUE}{y.count('Anorganik')}{RESET} sampel")
    print(f"{CYAN}" + "-"*80 + f"{RESET}")

    # Tampilkan 5 data fitur pertama
    print(f"\n{GREEN}[INFO] Menampilkan 5 sampel ekstraksi fitur warna RGB pertama:{RESET}")
    print(f"  {CYAN}+------------------+--------------------+------------------+----------------+{RESET}")
    print(f"  {CYAN}| Rerata Red (X1)  | Rerata Green (X2)  | Rerata Blue (X3) | Kategori Label |{RESET}")
    print(f"  {CYAN}+------------------+--------------------+------------------+----------------+{RESET}")
    for i in range(min(5, len(X))):
        color_label = GREEN if y[i] == "Organik" else BLUE
        print("  | {:<16.2f} | {:<18.2f} | {:<16.2f} | {}{:<14}{} |".format(X[i][0], X[i][1], X[i][2], color_label, y[i], RESET))
    print(f"  {CYAN}+------------------+--------------------+------------------+----------------+{RESET}")

    # Bagi Data (Train/Test)
    X_train, X_test, y_train, y_test = train_test_split_scratch(X, y, test_size=0.2, seed=1)
    print(f"\n{GREEN}[INFO] Pembagian Dataset (Split 80:20):{RESET}")
    print(f"  > Jumlah Data Latih (Train) : {BOLD}{len(X_train)}{RESET} gambar")
    print(f"  > Jumlah Data Uji (Test)    : {BOLD}{len(X_test)}{RESET} gambar")

    # Latih Decision Tree Classifier Scratch
    print(f"\n{CYAN}>>> Melatih Model Decision Tree Custom (Kedalaman Maks = 4)...{RESET}")
    clf = DecisionTreeClassifierScratch(max_depth=4, min_samples_split=2)
    clf.fit(X_train, y_train)
    print(f"{GREEN}[SUCCESS] Model berhasil dilatih secara mandiri dari nol.{RESET}")

    # Tampilkan Struktur Pohon Keputusan
    print("\n" + f"{MAGENTA}="*80 + f"{RESET}")
    print(f"{BOLD}{YELLOW}{'{:^80}'.format('STRUKTUR POHON KEPUTUSAN YANG TERBENTUK (PROSES SELEKSI)')}{RESET}")
    print(f"{MAGENTA}="*80 + f"{RESET}")
    print_decision_tree(clf.root, feature_names)
    print(f"{MAGENTA}="*80 + f"{RESET}")

    # Uji Model dengan Data Uji
    y_pred = clf.predict(X_test)
    metrics = evaluate_performance(y_test, y_pred)

    # Laporan metrik evaluasi
    print("\n" + f"{MAGENTA}+" + "="*78 + f"+{RESET}")
    print(f"{MAGENTA}|{RESET}{BOLD}{YELLOW}{'{:^78}'.format('LAPORAN EVALUASI KINERJA MODEL KEPUTUSAN')}{RESET}{MAGENTA}|{RESET}")
    print(f"{MAGENTA}+" + "="*78 + f"+{RESET}")
    print(f"{MAGENTA}|{RESET}  Akurasi Uji (Accuracy)    : {GREEN}{'{:<50.2f}'.format(metrics['accuracy'] * 100)}%{RESET} {MAGENTA}|{RESET}")
    print(f"{MAGENTA}|{RESET}  Presisi Uji (Precision)   : {GREEN}{'{:<50.2f}'.format(metrics['precision'] * 100)}%{RESET} {MAGENTA}|{RESET}")
    print(f"{MAGENTA}|{RESET}  Sensitivitas (Recall)     : {GREEN}{'{:<50.2f}'.format(metrics['recall'] * 100)}%{RESET} {MAGENTA}|{RESET}")
    print(f"{MAGENTA}|{RESET}  Skor Harmoni (F1-Score)   : {GREEN}{'{:<50.2f}'.format(metrics['f1'] * 100)}%{RESET} {MAGENTA}|{RESET}")
    print(f"{MAGENTA}+" + "-"*78 + f"+{RESET}")

    # Confusion Matrix
    matrix = metrics['matrix']
    print(f"{MAGENTA}|{RESET}{BOLD}{CYAN}{'{:^78}'.format('Matriks Kebingungan (Confusion Matrix)')}{RESET}{MAGENTA}|{RESET}")
    print(f"{MAGENTA}+" + "-"*78 + f"+{RESET}")
    print(f"{MAGENTA}|{RESET}                       Prediksi ORGANIK         Prediksi ANORGANIK          {MAGENTA}|{RESET}")
    print(f"{MAGENTA}|{RESET}  Aktual ORGANIK       {GREEN}{'{:<24}'.format(matrix['TP'])}{RESET} {RED}{'{:<27}'.format(matrix['FN'])}{RESET} {MAGENTA}|{RESET}")
    print(f"{MAGENTA}|{RESET}  Aktual ANORGANIK     {RED}{'{:<24}'.format(matrix['FP'])}{RESET} {BLUE}{'{:<27}'.format(matrix['TN'])}{RESET} {MAGENTA}|{RESET}")
    print(f"{MAGENTA}+" + "="*78 + f"+{RESET}")

    # Pengujian Gambar Berbasis Menu Pilihan yang Rapi
    input(f"\n{YELLOW}Tekan ENTER untuk masuk ke Modul Interaktif...{RESET}")
    
    # State: True = tampilkan daftar gambar + menu tambahan (main menu)
    #        False = hanya tampilkan menu tambahan (setelah klasifikasi)
    tampilkan_daftar = True
    options = []  # cache daftar gambar

    while True:
        # ----------------------------------------------------------------
        # Selalu perbarui daftar gambar dari folder
        # ----------------------------------------------------------------
        organik_imgs = sorted([f for f in os.listdir(dir_organik) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        anorganik_imgs = sorted([f for f in os.listdir(dir_anorganik) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        options = []
        for file in organik_imgs:
            options.append((os.path.join(dir_organik, file), file, "Organik"))
        for file in anorganik_imgs:
            options.append((os.path.join(dir_anorganik, file), file, "Anorganik"))

        # ----------------------------------------------------------------
        # Tampilkan menu sesuai state
        # ----------------------------------------------------------------
        if tampilkan_daftar:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{MAGENTA}={'='*78}={RESET}")
            print(f"{BOLD}{YELLOW}{'{:^80}'.format('MODUL INTERAKTIF KLASIFIKASI CITRA SAMPAH')}{RESET}")
            print(f"{MAGENTA}={'='*78}={RESET}")
            print(f"\n{BOLD}Daftar file gambar terdeteksi dalam dataset:{RESET}")
            for idx, (path, name, label) in enumerate(options):
                print("  [{:02d}] {}".format(idx + 1, name))

        if tampilkan_daftar:
            print(f"{MAGENTA}" + "-"*80 + f"{RESET}")
            print(f"{BOLD}{CYAN}Info: Masukkan nomor gambar (1-{len(options)}) untuk mengklasifikasikan, atau [0]/[A]/[C]/[X] untuk opsi lain.{RESET}")
        else:
            print(f"{MAGENTA}" + "-"*80 + f"{RESET}")

        pilihan = input("Pilih nomor / opsi: ").strip()
        if not pilihan:
            continue

        # ----------------------------------------------------------------
        # 1. Keluar
        # ----------------------------------------------------------------
        if pilihan.upper() == 'X':
            print("\n" + f"{MAGENTA}+" + "="*78 + f"+{RESET}")
            print(f"{MAGENTA}|{RESET}{BOLD}{GREEN}{'{:^78}'.format('Terima kasih! Tetap semangat menjaga kelestarian lingkungan hidup.')}{RESET}{MAGENTA}|{RESET}")
            print(f"{MAGENTA}+" + "="*78 + f"+{RESET}")
            try:
                cv2.destroyAllWindows()
            except Exception:
                pass
            break

        # ----------------------------------------------------------------
        # 2. Kembali ke daftar gambar (hanya muncul saat state kontinu)
        # ----------------------------------------------------------------
        if pilihan.upper() == 'M':
            tampilkan_daftar = True
            continue

        # ----------------------------------------------------------------
        # 3. Slide Teori/Matematika
        # ----------------------------------------------------------------
        if pilihan == '0':
            tampilkan_cara_kerja()
            tampilkan_daftar = True
            continue

        # ----------------------------------------------------------------
        # 4. Uji gambar kustom
        # ----------------------------------------------------------------
        if pilihan.upper() == 'C':
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{MAGENTA}={'='*78}={RESET}")
            print(f"{BOLD}{YELLOW}{'{:^80}'.format('UJI FILE GAMBAR KUSTOM')}{RESET}")
            print(f"{MAGENTA}={'='*78}={RESET}")
            custom_path = input(f"\nMasukkan jalur file gambar kustom Anda: ").strip()

            # Validasi jalur
            path_check = custom_path
            if not os.path.exists(path_check):
                path_check = os.path.join(base_dir, custom_path)
            if not os.path.exists(path_check):
                if custom_path.startswith("TUBES/"):
                    path_check = os.path.join(base_dir, custom_path.replace("TUBES/", ""))
                elif custom_path.startswith("TUBES\\"):
                    path_check = os.path.join(base_dir, custom_path.replace("TUBES\\", ""))

            if not os.path.exists(path_check):
                print(f"{RED}[ERR] File gambar kustom tidak ditemukan pada jalur tersebut!{RESET}")
                tampilkan_daftar = True
                continue

            test_img = cv2.imread(path_check)
            if test_img is None:
                print(f"{RED}[ERR] Gagal memuat file! File rusak atau format tidak didukung.{RESET}")
                tampilkan_daftar = True
                continue

            try:
                cv2.destroyAllWindows()
                cv2.namedWindow("Citra Sampah Uji", cv2.WINDOW_NORMAL)
                cv2.imshow("Citra Sampah Uji", test_img)
                cv2.waitKey(1)
                print(f"\n[GUI] Membuka jendela visual untuk citra: {os.path.basename(path_check)}")
            except Exception:
                print(f"\n[INFO] Menjalankan sistem headless. Prediksi langsung dicetak.")

            img_resized = cv2.resize(test_img, (64, 64))
            tb = np.mean(img_resized[:, :, 0])
            tg = np.mean(img_resized[:, :, 1])
            tr = np.mean(img_resized[:, :, 2])

            fitur_uji = [tr, tg, tb]
            kategori_prediksi, path_steps = clf.predict_with_path(fitur_uji, feature_names)

            print(f"\n{CYAN}>>> Rerata RGB yang Diekstrak:{RESET} R={tr:.2f}, G={tg:.2f}, B={tb:.2f}")
            print(f"{YELLOW}>>> Alur Keputusan Decision Tree:{RESET}")
            for step_idx, step in enumerate(path_steps):
                if "=> [TRUE]" in step:
                    formatted_step = step.replace("=> [TRUE]", f"=> {GREEN}TRUE (Belok Kiri){RESET}")
                else:
                    formatted_step = step.replace("=> [FALSE]", f"=> {RED}FALSE (Belok Kanan){RESET}")
                print(f"    Langkah {step_idx+1}: {formatted_step}")

            color_pred = GREEN if kategori_prediksi == "Organik" else BLUE
            print(f"\n{color_pred}+" + "-"*68 + f"+{RESET}")
            print(f"{color_pred}|{RESET}{BOLD}{'{:^68}'.format('HASIL KLASIFIKASI CITRA SAMPAH KUSTOM')}{RESET}{color_pred}|{RESET}")
            print(f"{color_pred}+" + "-"*68 + f"+{RESET}")
            print(f"{color_pred}|{RESET}  Nama File    : {BOLD}{'{:<48}'.format(os.path.basename(path_check))}{RESET} {color_pred}|{RESET}")
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

            # Langsung lanjut ke menu tambahan tanpa clearing
            tampilkan_daftar = False
            continue

        # ----------------------------------------------------------------
        # 5. Multi-Select / Batch Klasifikasi (nomor gambar / A)
        # ----------------------------------------------------------------
        valid_indices = []

        if pilihan.upper() == 'A':
            valid_indices = list(range(len(options)))
        else:
            chosen_numbers = []
            parts = pilihan.split(",")
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                if "-" in part:
                    subparts = part.split("-")
                    if len(subparts) == 2 and subparts[0].strip().isdigit() and subparts[1].strip().isdigit():
                        start = int(subparts[0].strip())
                        end = int(subparts[1].strip())
                        if start <= end:
                            chosen_numbers.extend(range(start, end + 1))
                        else:
                            chosen_numbers.extend(range(start, end - 1, -1))
                    else:
                        print(f"{RED}[WARN] Format rentang '{part}' tidak valid!{RESET}")
                elif part.isdigit():
                    chosen_numbers.append(int(part))
                else:
                    print(f"{RED}[WARN] Format '{part}' tidak dikenali!{RESET}")

            for num in chosen_numbers:
                if 1 <= num <= len(options):
                    valid_indices.append(num - 1)
                else:
                    print(f"{RED}[WARN] Nomor gambar [{num:02d}] di luar jangkauan (1-{len(options)})!{RESET}")

        if not valid_indices:
            print(f"{RED}[WARN] Tidak ada gambar valid yang dipilih. Silakan coba lagi.{RESET}")
            continue

        # Jalankan klasifikasi untuk semua gambar terpilih
        for rank, idx in enumerate(valid_indices):
            selected_path, name, label = options[idx]

            print(f"\n{BOLD}{MAGENTA}" + "-"*80 + f"{RESET}")
            print(f"{BOLD}{YELLOW}  MEMPROSES CITRA [{rank+1}/{len(valid_indices)}]: {name}{RESET}")
            print(f"{BOLD}{MAGENTA}" + "-"*80 + f"{RESET}")

            test_img = cv2.imread(selected_path)
            if test_img is None:
                print(f"{RED}[ERR] File '{name}' gagal dibaca!{RESET}")
                continue

            try:
                cv2.destroyAllWindows()
                cv2.namedWindow("Citra Sampah Uji", cv2.WINDOW_NORMAL)
                cv2.imshow("Citra Sampah Uji", test_img)
                cv2.waitKey(1)
                print(f"[GUI] Menampilkan jendela '{name}'...")
            except Exception:
                print("[INFO] Menjalankan sistem headless (tanpa GUI).")

            img_resized = cv2.resize(test_img, (64, 64))
            tb = np.mean(img_resized[:, :, 0])
            tg = np.mean(img_resized[:, :, 1])
            tr = np.mean(img_resized[:, :, 2])

            fitur_uji = [tr, tg, tb]
            kategori_prediksi, path_steps = clf.predict_with_path(fitur_uji, feature_names)

            print(f"\n{CYAN}>>> Rerata RGB yang Diekstrak:{RESET} R={tr:.2f}, G={tg:.2f}, B={tb:.2f}")
            print(f"{YELLOW}>>> Alur Keputusan Decision Tree:{RESET}")
            for step_idx, step in enumerate(path_steps):
                if "=> [TRUE]" in step:
                    formatted_step = step.replace("=> [TRUE]", f"=> {GREEN}TRUE (Belok Kiri){RESET}")
                else:
                    formatted_step = step.replace("=> [FALSE]", f"=> {RED}FALSE (Belok Kanan){RESET}")
                print(f"    Langkah {step_idx+1}: {formatted_step}")

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

            # Jika batch mode dan masih ada gambar berikutnya, pakai jeda singkat
            if len(valid_indices) > 1 and rank < len(valid_indices) - 1:
                input(f"\n{YELLOW}Tekan ENTER untuk memproses gambar berikutnya [{rank+2}/{len(valid_indices)}]...{RESET}")

        # Setelah semua gambar selesai -> tampilkan 2 pilihan
        print(f"\n{BOLD}  [1]{RESET} Lanjut pilih gambar lain")
        print(f"  {BOLD}[2]{RESET} Stop & Keluar program")
        print(f"{MAGENTA}" + "-"*80 + f"{RESET}")

        while True:
            lanjut = input("Pilihan (1/2): ").strip()
            if lanjut == "1":
                tampilkan_daftar = True
                break
            elif lanjut == "2":
                print("\n" + f"{MAGENTA}+" + "="*78 + f"+{RESET}")
                print(f"{MAGENTA}|{RESET}{BOLD}{GREEN}{'{:^78}'.format('Terima kasih! Tetap semangat menjaga kelestarian lingkungan hidup.')}{RESET}{MAGENTA}|{RESET}")
                print(f"{MAGENTA}+" + "="*78 + f"+{RESET}")
                try:
                    cv2.destroyAllWindows()
                except Exception:
                    pass
                import sys
                sys.exit(0)
            else:
                print(f"{RED}[WARN] Masukkan 1 untuk lanjut atau 2 untuk stop.{RESET}")
