import random  # library untuk bilangan acak
import math    # library fungsi matematika

# Parameter Genetic Algorithm
POP = 20       # jumlah individu dalam populasi
GEN = 100      # jumlah generasi (iterasi)
PC = 0.8       # probabilitas crossover
PM = 0.01      # probabilitas mutasi

# ===== INPUT DARI USER =====
print("="*40)  # garis pembatas
print("PROGRAM GENETIC ALGORITHM")  # judul program
print("Mencari Minimum Fungsi f(x1, x2)")  # deskripsi
print("="*40)

# input batas domain
x1_min = float(input("Masukkan batas bawah x1: "))  # batas bawah x1
x1_max = float(input("Masukkan batas atas x1: "))   # batas atas x1
x2_min = float(input("Masukkan batas bawah x2: "))  # batas bawah x2
x2_max = float(input("Masukkan batas atas x2: "))   # batas atas x2

# simpan domain ke variabel global
MIN_X1, MAX_X1 = x1_min, x1_max
MIN_X2, MAX_X2 = x2_min, x2_max

# tampilkan domain
print(f"\nDomain: x1 ∈ [{MIN_X1}, {MAX_X1}], x2 ∈ [{MIN_X2}, {MAX_X2}]") # simbol ∈ anggota himpunan
print("Memproses...\n")

# ===== INISIALISASI POPULASI =====
def init_pop():
    # membuat populasi berisi kromosom biner 32 bit
    return [''.join(random.choice('01') for _ in range(32)) for _ in range(POP)]

# ===== DECODE KROMOSOM =====
def decode(c):
    x1_bin = c[:16]       # ambil 16 bit pertama (x1)
    x2_bin = c[16:]       # ambil 16 bit terakhir (x2)
    
    x1_int = int(x1_bin, 2)  # ubah biner ke desimal
    x2_int = int(x2_bin, 2)
    
    # ubah ke nilai real sesuai domain
    x1 = MIN_X1 + (x1_int / (2**16 - 1)) * (MAX_X1 - MIN_X1)
    x2 = MIN_X2 + (x2_int / (2**16 - 1)) * (MAX_X2 - MIN_X2)
    
    return x1, x2  # hasil decoding

# ===== FUNGSI OBJEKTIF =====
def f(x1, x2):
    try:
        # fungsi yang akan diminimalkan(persamaan fungsi)
        return -(math.sin(x1)*math.cos(x2)*math.tan(x1+x2)
                 + 0.5*math.exp(1-math.sqrt(x2**2)))
    except:
        return float('inf')  # jika error (tan tidak valid)

# ===== FITNESS FUNCTION =====
def fit(c):
    x1, x2 = decode(c)         # decode kromosom
    return 1/(1+abs(f(x1,x2))) # ubah minimasi → maksimasi

# ===== SELEKSI (ROULETTE) =====
def select(pop):
    total = sum(fit(c) for c in pop)  # total fitness
    r, s = random.random(), 0         # angka acak & kumulatif
    
    for c in pop:
        s += fit(c)/total             # probabilitas kumulatif
        if r <= s:                    # pilih berdasarkan peluang
            return c

# ===== CROSSOVER + MUTASI =====
def evolve(p1, p2):
    if random.random() < PC:          # cek crossover
        pt = random.randint(1, 31)    # titik potong
        p1 = p1[:pt] + p2[pt:]        # anak 1
        p2 = p2[:pt] + p1[pt:]        # anak 2
    
    def mutate(c):
        # mutasi tiap bit (flip 0↔1)
        return ''.join(
            ('1' if b=='0' else '0') if random.random()<PM else b
            for b in c
        )
    
    return mutate(p1), mutate(p2)     # hasil evolusi

# ===== GENETIC ALGORITHM =====
def GA():
    pop = init_pop()                  # populasi awal
    
    for generation in range(GEN):     # loop generasi
        new = []
        
        while len(new) < POP:
            p1 = select(pop)          # pilih parent 1
            p2 = select(pop)          # pilih parent 2
            c1, c2 = evolve(p1, p2)   # crossover + mutasi
            new += [c1, c2]           # tambah ke populasi baru
        
        pop = new[:POP]               # update populasi
        
        # tampilkan progres tiap 20 generasi
        if (generation+1) % 20 == 0:
            best_c = max(pop, key=fit)  # ambil terbaik
            x1, x2 = decode(best_c)
            print(f"Generasi {generation+1}: x1={x1:.4f}, x2={x2:.4f}, f={f(x1,x2):.4f}")
    
    return max(pop, key=fit)          # hasil terbaik akhir

# ===== PROGRAM UTAMA =====
print("="*40)
print("MENJALANKAN GENETIC ALGORITHM...")
print("="*40)

best = GA()               # jalankan GA
x1, x2 = decode(best)     # decode solusi terbaik

# tampilkan hasil akhir
print("\n" + "="*40)
print("HASIL AKHIR")
print("="*40)
print(f"Kromosom Terbaik: {best}")
print(f"x1 = {x1}")
print(f"x2 = {x2}")
print(f"Nilai Minimum f(x1,x2) = {f(x1, x2)}")
print("="*40)