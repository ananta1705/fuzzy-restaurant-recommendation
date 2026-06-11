import pandas as pd  # untuk membaca & menulis file Excel

# ========================
# FUZZIFICATION
# ========================

def fuzzifikasi_servis(x):
    # rendah
    if x <= 50:
        rendah = 1
    elif 50 < x < 70:
        rendah = (70 - x) / 20
    else:
        rendah = 0

    # sedang (segitiga)
    if 30 < x < 50:
        sedang = (x - 30) / 20
    elif 50 <= x < 70:
        sedang = (70 - x) / 20
    else:
        sedang = 0

    # tinggi
    if x >= 70:
        tinggi = 1
    elif 50 < x < 70:
        tinggi = (x - 50) / 20
    else:
        tinggi = 0

    return rendah, sedang, tinggi


def fuzzifikasi_harga(x):
    # murah
    if x <= 35000:
        murah = 1
    elif 35000 < x < 45000:
        murah = (45000 - x) / 10000
    else:
        murah = 0

    # sedang (segitiga)
    if 30000 < x < 40000:
        sedang = (x - 30000) / 10000
    elif 40000 <= x < 50000:
        sedang = (50000 - x) / 10000
    else:
        sedang = 0

    # mahal
    if x >= 50000:
        mahal = 1
    elif 40000 < x < 50000:
        mahal = (x - 40000) / 10000
    else:
        mahal = 0

    return murah, sedang, mahal


# ========================
# INFERENSI (9 RULE)
# ========================

def inferensi(s_r, s_s, s_t, h_m, h_s, h_ma):
    rules = [
        min(s_t, h_m),   # tinggi + murah → sangat baik
        min(s_t, h_s),   # tinggi + sedang → baik
        min(s_t, h_ma),  # tinggi + mahal → cukup

        min(s_s, h_m),   # sedang + murah → baik
        min(s_s, h_s),   # sedang + sedang → cukup
        min(s_s, h_ma),  # sedang + mahal → kurang

        min(s_r, h_m),   # rendah + murah → cukup
        min(s_r, h_s),   # rendah + sedang → kurang
        min(s_r, h_ma)   # rendah + mahal → buruk
    ]
    return rules


# ========================
# DEFUZZIFICATION (SUGENO)
# ========================

def defuzzifikasi(rules):
    # nilai output untuk setiap rule
    z = [90, 80, 60, 80, 60, 40, 60, 40, 30]

    total = sum(rules)

    if total == 0:
        return 0

    return sum(r * z_i for r, z_i in zip(rules, z)) / total


# ========================
# HITUNG SCORE
# ========================

def hitung_score(servis, harga):
    s_r, s_s, s_t = fuzzifikasi_servis(servis)
    h_m, h_s, h_ma = fuzzifikasi_harga(harga)

    rules = inferensi(s_r, s_s, s_t, h_m, h_s, h_ma)

    return defuzzifikasi(rules)


# ========================
# PROGRAM UTAMA
# ========================

def main():
    # baca file Excel
    data = pd.read_excel("restoran.xlsx")

    hasil = []

    # looping semua data
    for i in range(len(data)):
        servis = data.iloc[i, 1]
        harga = data.iloc[i, 2]

        score = hitung_score(servis, harga)
        hasil.append(score)

    # tambah kolom score
    data["Score"] = hasil

    # urutkan dari terbesar
    data = data.sort_values(by="Score", ascending=False)

    # ambil 5 terbaik
    top5 = data.head(5)

    print("\n===== TOP 5 RESTORAN =====")
    print(top5)

    # simpan ke file
    top5.to_excel("peringkat.xlsx", index=False)

    print("\nOutput berhasil disimpan ke peringkat.xlsx")


# jalankan program
if __name__ == "__main__":
    main()