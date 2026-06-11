# Import Library
import os
import cv2
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Path dataset relatif terhadap lokasi script test.py
base_dir = os.path.dirname(os.path.abspath(__file__))
dir_organik = os.path.join(base_dir, "dataset", "Organik")
dir_anorganik = os.path.join(base_dir, "dataset", "Anorganik")

# Buat folder jika belum ada
os.makedirs(dir_organik, exist_ok=True)
os.makedirs(dir_anorganik, exist_ok=True)

# Menyimpan fitur dan label
X = []
y = []

# Membaca gambar organik
for file in os.listdir(dir_organik):
    img_path = os.path.join(dir_organik, file)
    img = cv2.imread(img_path)
    if img is None:
        continue
    img = cv2.resize(img, (64, 64))

    # Ekstraksi fitur sederhana
    mean_r = np.mean(img[:,:,2])
    mean_g = np.mean(img[:,:,1])
    mean_b = np.mean(img[:,:,0])

    X.append([mean_r, mean_g, mean_b])
    y.append("Organik")

# Membaca gambar anorganik
for file in os.listdir(dir_anorganik):
    img_path = os.path.join(dir_anorganik, file)
    img = cv2.imread(img_path)
    if img is None:
        continue
    img = cv2.resize(img, (64, 64))

    mean_r = np.mean(img[:,:,2])
    mean_g = np.mean(img[:,:,1])
    mean_b = np.mean(img[:,:,0])

    X.append([mean_r, mean_g, mean_b])
    y.append("Anorganik")

# Memastikan dataset tidak kosong sebelum training
if len(X) == 0:
    print("Dataset kosong! Silakan masukkan file gambar ke dalam folder berikut:")
    print(f"  - Organik  : {dir_organik}")
    print(f"  - Anorganik: {dir_anorganik}")
    import sys
    sys.exit(0)

# Membagi data train dan test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Membuat model Decision Tree
model = DecisionTreeClassifier()

# Training
model.fit(X_train, y_train)

# Prediksi
prediksi = model.predict(X_test)

# Akurasi
akurasi = accuracy_score(y_test, prediksi)

print("Akurasi:", akurasi)