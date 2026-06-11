# ==============================================================================
# KLASIFIKASI JENIS SAMPAH ORGANIK DAN ANORGANIK DENGAN DECISION TREE DARI SCRATCH
# Untuk Mendukung Pengelolaan Lingkungan Hidup Berkelanjutan
# ==============================================================================

import random
import math

# ------------------------------------------------------------------------------
# 1. GENERATOR DATASET BUATAN (SYNTHETIC DATASET GENERATION)
# ------------------------------------------------------------------------------
def generate_dataset(num_samples=100, seed=42):
    """
    Menghasilkan data buatan dengan 3 fitur utama:
    1. Kandungan Air / Kelembapan (0 - 100 %)
    2. Kekerasan / Rigiditas (0 - 100)
    3. Kecepatan Degradasi / Penguraian (0 - 100)
    
    Label: 'Organik' atau 'Anorganik'
    """
    random.seed(seed)
    X = []
    y = []
    
    # Menghasilkan data Organik
    # Karakteristik: Kelembapan tinggi, Kekerasan rendah, Degradasi cepat
    for _ in range(num_samples // 2):
        kelembapan = round(random.uniform(55, 98), 2)
        kekerasan = round(random.uniform(5, 35), 2)
        degradasi = round(random.uniform(60, 95), 2)
        X.append([kelembapan, kekerasan, degradasi])
        y.append("Organik")
        
    # Menghasilkan data Anorganik
    # Karakteristik: Kelembapan rendah, Kekerasan tinggi, Degradasi lambat
    for _ in range(num_samples // 2):
        kelembapan = round(random.uniform(2, 40), 2)
        kekerasan = round(random.uniform(25, 95), 2)
        degradasi = round(random.uniform(2, 25), 2)
        X.append([kelembapan, kekerasan, degradasi])
        y.append("Anorganik")
        
    # Menambahkan variasi/noise (misalnya: kayu/ranting pohon - organik tapi keras & degradasi lambat)
    # Atau tisu basah / plastik tipis - anorganik/campuran tapi kelembapan agak tinggi & kekerasan rendah
    for _ in range(10): # 10 sample noise
        # Organik yang agak keras dan lambat terurai (misal: ranting kayu kering)
        kelembapan = round(random.uniform(15, 40), 2)
        kekerasan = round(random.uniform(50, 75), 2)
        degradasi = round(random.uniform(30, 55), 2)
        X.append([kelembapan, kekerasan, degradasi])
        y.append("Organik")
        
        # Anorganik yang lunak dan lembab (misal: plastik basah/tisu basah bekas)
        kelembapan = round(random.uniform(45, 70), 2)
        kekerasan = round(random.uniform(10, 25), 2)
        degradasi = round(random.uniform(5, 20), 2)
        X.append([kelembapan, kekerasan, degradasi])
        y.append("Anorganik")

    # Acak posisi data agar tidak terurut
    combined = list(zip(X, y))
    random.shuffle(combined)
    X_shuffled, y_shuffled = zip(*combined)
    
    return list(X_shuffled), list(y_shuffled)


# ------------------------------------------------------------------------------
# 2. ALGORITMA DECISION TREE DARI GORESAN (FROM SCRATCH)
# ------------------------------------------------------------------------------
class Node:
    """Representasi Node dalam Decision Tree"""
    def __init__(self, feature_idx=None, threshold=None, left=None, right=None, value=None):
        self.feature_idx = feature_idx  # Indeks fitur pemisah
        self.threshold = threshold      # Nilai pembatas (threshold) pemisahan
        self.left = left                # Node anak kiri
        self.right = right              # Node anak kanan
        self.value = value              # Nilai kelas (Hanya diisi jika Node merupakan Leaf/Daun)

    def is_leaf(self):
        return self.value is not None


def calculate_gini(labels):
    """Menghitung Gini Impurity dari sekumpulan label kelas"""
    if not labels:
        return 0
    total = len(labels)
    counts = {}
    for label in labels:
        counts[label] = counts.get(label, 0) + 1
    
    # Formula Gini = 1 - sum(p_i^2)
    gini = 1.0 - sum((count / total) ** 2 for count in counts.values())
    return gini


class DecisionTreeClassifierScratch:
    """Implementasi Decision Tree Classifier tanpa Library Eksternal"""
    def __init__(self, max_depth=5, min_samples_split=2):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.root = None

    def fit(self, X, y):
        """Melatih model Decision Tree menggunakan data latih"""
        self.root = self._build_tree(X, y, depth=0)

    def _build_tree(self, X, y, depth):
        num_samples = len(X)
        if num_samples == 0:
            return None

        num_features = len(X[0])
        unique_classes = set(y)

        # Hentikan rekursi jika kriteria terpenuhi (Pure node, Max Depth, atau Sample tidak cukup)
        if (depth >= self.max_depth or 
            len(unique_classes) == 1 or 
            num_samples < self.min_samples_split):
            # Tentukan daun berdasarkan kelas terbanyak (majority vote)
            leaf_value = max(unique_classes, key=y.count)
            return Node(value=leaf_value)

        # Cari pembagian (split) terbaik berdasarkan Gini Impurity terendah
        best_idx, best_thresh = self._best_split(X, y, num_features)
        if best_idx is None:
            # Jika tidak ada split yang layak, buat node daun
            leaf_value = max(unique_classes, key=y.count)
            return Node(value=leaf_value)

        # Lakukan pemisahan dataset
        left_X, left_y, right_X, right_y = self._split(X, y, best_idx, best_thresh)

        # Jika salah satu cabang kosong, kembalikan daun dengan kelas terbanyak
        if not left_X or not right_X:
            leaf_value = max(unique_classes, key=y.count)
            return Node(value=leaf_value)

        # Bangun sub-pohon kiri dan kanan secara rekursif
        left_child = self._build_tree(left_X, left_y, depth + 1)
        right_child = self._build_tree(right_X, right_y, depth + 1)

        return Node(feature_idx=best_idx, threshold=best_thresh, left=left_child, right=right_child)

    def _best_split(self, X, y, num_features):
        best_gini = 999.0
        best_idx = None
        best_thresh = None

        for idx in range(num_features):
            # Ambil semua nilai unik dari fitur ini
            values = sorted(list(set(sample[idx] for sample in X)))
            
            # Cari calon threshold (titik tengah antara nilai yang berurutan)
            thresholds = []
            for i in range(len(values) - 1):
                thresholds.append((values[i] + values[i+1]) / 2.0)

            # Jika nilai unik hanya 1, gunakan nilai itu sendiri
            if not thresholds and values:
                thresholds = [values[0]]

            for thresh in thresholds:
                left_X, left_y, right_X, right_y = self._split(X, y, idx, thresh)
                if not left_y or not right_y:
                    continue

                # Hitung Weighted Gini Impurity dari split ini
                p_left = len(left_y) / len(y)
                p_right = len(right_y) / len(y)
                gini_split = p_left * calculate_gini(left_y) + p_right * calculate_gini(right_y)

                if gini_split < best_gini:
                    best_gini = gini_split
                    best_idx = idx
                    best_thresh = thresh

        return best_idx, best_thresh

    def _split(self, X, y, feature_idx, threshold):
        """Membagi data berdasarkan apakah nilai fitur <= threshold"""
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
        """Memprediksi kelas untuk sekumpulan data uji"""
        return [self._traverse(sample, self.root) for sample in X]

    def _traverse(self, sample, node):
        """Berjalan menyusuri pohon keputusan sampai ke daun"""
        if node.is_leaf():
            return node.value
        if sample[node.feature_idx] <= node.threshold:
            return self._traverse(sample, node.left)
        else:
            return self._traverse(sample, node.right)


# ------------------------------------------------------------------------------
# 3. PEMBAGIAN DATA & EVALUASI KINERJA (TRAIN/TEST SPLIT & METRICS FROM SCRATCH)
# ------------------------------------------------------------------------------
def train_test_split_scratch(X, y, test_size=0.2, seed=42):
    """Membagi dataset menjadi set pelatihan dan set pengujian"""
    random.seed(seed)
    combined = list(zip(X, y))
    random.shuffle(combined)
    
    split_idx = int(len(combined) * (1 - test_size))
    
    train_data = combined[:split_idx]
    test_data = combined[split_idx:]
    
    X_train, y_train = zip(*train_data)
    X_test, y_test = zip(*test_data)
    
    return list(X_train), list(X_test), list(y_train), list(y_test)


def evaluate_performance(y_true, y_pred):
    """Menghitung akurasi, presisi, recall, f1-score, dan confusion matrix"""
    total = len(y_true)
    accuracy = sum(1 for t, p in zip(y_true, y_pred) if t == p) / total
    
    # Untuk Kelas "Organik" (Positif) dan "Anorganik" (Negatif)
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
# 4. VISUALISASI POHON KEPUTUSAN (DECISION TREE VISUALIZER)
# ------------------------------------------------------------------------------
def print_decision_tree(node, feature_names, depth=0, prefix="Root"):
    """Mencetak struktur pohon keputusan secara visual di terminal"""
    if node is None:
        return
    
    indent = "    " * depth
    if node.is_leaf():
        print(f"{indent}\\-- [Daun] {prefix} => HASIL: {node.value}")
        return
    
    feat_name = feature_names[node.feature_idx]
    print(f"{indent}|-- [Cabang] {prefix} => JIKA {feat_name} <= {node.threshold:.2f}")
    print_decision_tree(node.left, feature_names, depth + 1, "Kiri (True)")
    print_decision_tree(node.right, feature_names, depth + 1, "Kanan (False)")


# ------------------------------------------------------------------------------
# 5. ALUR UTAMA PROGRAM (MAIN APPLICATION FLOW)
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    print("="*80)
    print(" PROGRAM KLASIFIKASI SAMPAH ORGANIK & ANORGANIK DENGAN DECISION TREE DARI NOL")
    print(" Untuk Mendukung Pengelolaan Lingkungan Hidup Berkelanjutan")
    print("="*80)
    
    # Nama Fitur
    feature_names = [
        "Kelembapan / Kandungan Air (%)",
        "Kekerasan / Rigiditas (0-100)",
        "Kecepatan Degradasi / Penguraian (0-100)"
    ]
    
    # Langkah 1: Generate Dataset
    print("\n[Langkah 1] Membuat dataset buatan...")
    X, y = generate_dataset(num_samples=120, seed=42)
    print(f"Total dataset: {len(X)} sampel.")
    print(f"  - Sampah Organik  : {y.count('Organik')} sampel")
    print(f"  - Sampah Anorganik: {y.count('Anorganik')} sampel")
    
    # Tampilkan 5 contoh data pertama
    print("\n5 Sampel Pertama Dataset:")
    print(f"  {'Kelembapan':<12} | {'Kekerasan':<10} | {'Degradasi':<10} | {'Kategori':<10}")
    print("  " + "-"*52)
    for i in range(5):
        print(f"  {X[i][0]:<12.2f} | {X[i][1]:<10.2f} | {X[i][2]:<10.2f} | {y[i]:<10}")
        
    # Langkah 2: Bagi Dataset (Train/Test Split)
    print("\n[Langkah 2] Membagi dataset menjadi Train (80%) dan Test (20%)...")
    X_train, X_test, y_train, y_test = train_test_split_scratch(X, y, test_size=0.2, seed=42)
    print(f"Data latih (Train): {len(X_train)} sampel")
    print(f"Data uji (Test)   : {len(X_test)} sampel")
    
    # Langkah 3: Melatih Model (Fit)
    print("\n[Langkah 3] Melatih model Decision Tree (Maks Kedalaman = 3)...")
    clf = DecisionTreeClassifierScratch(max_depth=3, min_samples_split=2)
    clf.fit(X_train, y_train)
    print("Model berhasil dilatih.")
    
    # Langkah 4: Visualisasi Struktur Pohon Keputusan
    print("\n[Langkah 4] Visualisasi Struktur Pohon Keputusan yang Terbentuk:")
    print("-" * 60)
    print_decision_tree(clf.root, feature_names)
    print("-" * 60)
    
    # Langkah 5: Pengujian Model & Evaluasi Kinerja
    print("\n[Langkah 5] Menguji model dengan data uji...")
    y_pred = clf.predict(X_test)
    metrics = evaluate_performance(y_test, y_pred)
    
    print("\nHASIL EVALUASI MODEL:")
    print(f"  Akurasi   : {metrics['accuracy'] * 100:.2f} %")
    print(f"  Presisi   : {metrics['precision'] * 100:.2f} %")
    print(f"  Recall    : {metrics['recall'] * 100:.2f} %")
    print(f"  F1-Score  : {metrics['f1'] * 100:.2f} %")
    
    # Confusion Matrix
    matrix = metrics['matrix']
    print("\nMatriks Kebingungan (Confusion Matrix):")
    print("                    Prediksi ORGANIK    Prediksi ANORGANIK")
    print(f"Aktual ORGANIK       {matrix['TP']:<19} {matrix['FN']:<18}")
    print(f"Aktual ANORGANIK     {matrix['FP']:<19} {matrix['TN']:<18}")
    
    # Langkah 6: Simulasi Pengguna Interaktif
    while True:
        print("\n" + "="*50)
        print("          SIMULASI INTERAKTIF KLASIFIKASI SAMPAH")
        print("="*50)
        print("Masukkan karakteristik sampah untuk diprediksi secara real-time:")
        try:
            val_kelembapan = float(input("1. Kandungan Air / Kelembapan (0 - 100 %): "))
            val_kekerasan = float(input("2. Kekerasan / Kekakuan (0 - 100): "))
            val_degradasi = float(input("3. Kecepatan Degradasi / Penguraian (0 - 100): "))
            
            sample = [val_kelembapan, val_kekerasan, val_degradasi]
            hasil = clf.predict([sample])[0]
            
            print("-" * 50)
            print(f"HASIL PREDIKSI: Sampah tersebut adalah [ {hasil.upper()} ]")
            print("-" * 50)
            
            if hasil == "Organik":
                print("Rekomendasi Pengelolaan:")
                print("  - Dapat diproses menjadi pupuk kompos organik.")
                print("  - Dapat dijadikan makanan budidaya ulat maggot (Black Soldier Fly).")
                print("  - Dapat diolah menjadi eco-enzyme untuk pembersih ramah lingkungan.")
            else:
                print("Rekomendasi Pengelolaan:")
                print("  - Bersihkan lalu pisahkan berdasarkan kategori (plastik, kaca, logam, kertas).")
                print("  - Salurkan ke Bank Sampah terdekat agar masuk alur daur ulang pabrik.")
                print("  - Kurangi penggunaan plastik sekali pakai di masa mendatang.")
            
        except ValueError:
            print("Input tidak valid! Pastikan Anda memasukkan angka.")
            
        print("\n" + "-"*50)
        pilihan = input("Apakah Anda ingin mencoba lagi? (y/n): ").strip().lower()
        if pilihan != 'y':
            print("\nTerima kasih telah berkontribusi menjaga kelestarian lingkungan hidup!")
            print("="*50)
            break
