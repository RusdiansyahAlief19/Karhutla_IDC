# Temuan dan Pengujian Hipotesis (H1–H6)

Dokumen ini mencatat hasil pengujian empiris enam hipotesis kerja untuk kompetisi IDC Dateraquest 2.0 (subtema Preservasi Ekosistem Tropis, wilayah Sumatera 2015–2026). Seluruh angka bersumber langsung dari panel data interim yang telah terekonsiliasi (`fact_kab_month_interim.csv` dan `fact_kab_year_interim.csv`), tanpa imputasi liar dan tanpa menyamakan metrik deteksi hotspot dengan hektare luas terbakar.

---

## Ringkasan Status Hipotesis

| ID | Hipotesis Singkat | Status | Bukti Kunci |
|---|---|---|---|
| **H1** | Sebaran titik panas 2026 lebih menyebar dibanding 2019 | **Tidak didukung** | Pada jendela Jan–Okt, HHI kabupaten 2026 (0,1081) lebih tinggi +75,2% dibanding 2019 (0,0617); Sumsel mendominasi 58,7% titik panas Sumatera di 2026. |
| **H2** | Kebakaran di pesisir timur didominasi oleh lahan gambut | **Didukung** | Riau (78,5%) dan Jambi (68,3%) didominasi gambut; Sumsel mencatat luasan mutlak gambut terbakar tertinggi (307.204,2 ha). Sebaliknya Lampung, Babel, Bengkulu >95% di lahan mineral. |
| **H3** | Anomali curah hujan dan ONI berkorelasi terbalik dengan titik panas (lag 0–3) | **Tidak konklusif** | Data curah hujan spasial (CHIRPS) belum masuk pipeline per cut-off 18 November 2026; nilai hujan dibiarkan NaN sesuai kaidah integritas data. |
| **H4** | Sebaran titik panas terkonsentrasi secara ekstrem pada segelintir kabupaten (Pareto) | **Didukung** | Hanya 8 dari 154 kabupaten (5,2%) menyumbang 50,6% titik panas se-Sumatera 2015–2026. Ogan Komering Ilir sendirian menyumbang 23,2%. |
| **H5** | Terdapat kabupaten kronis yang persisten terbakar berulang setiap tahun | **Didukung** | Dengan definisi apriori $N \ge 6$ dari 10 tahun (2015–2024), teridentifikasi 11 kabupaten kronis, dipimpin Musi Banyuasin dan Musi Rawas (9 dari 10 tahun). |
| **H6** | Pola puncak musim kebakaran berbeda antara wilayah utara (bimodal) dan selatan (unimodal) | **Didukung** | Riau dan Aceh mengalami dua puncak (Feb–Mar dan Jul–Agt), sedangkan Sumatera Selatan dan Lampung terpusat ekstrem pada satu puncak tajam (Sep–Okt, mencapai 79% di Sumsel). |

---

## Rincian dan Tabel Bukti per Hipotesis

### H1. Konsentrasi Titik Panas 2026 vs 2019 (Jendela Januari–Oktober)

> **Status: Tidak didukung**  
> *Kalimat temuan:* Pada jendela pengamatan Januari hingga Oktober, persebaran titik panas tahun 2026 tidak lebih menyebar melainkan terasosiasi dengan tingkat konsentrasi spasial yang lebih tinggi dibanding 2019, di mana Sumatera Selatan menyumbang 58,7% dari total deteksi se-Sumatera.

Karena data tahun 2026 memiliki cut-off 31 Oktober 2026, perbandingan terhadap 2019 dilakukan secara berimbang pada jendela yang sama (Januari–Oktober).

| Metrik Konsentrasi | 2019 (Jan–Okt) | 2026 (Jan–Okt) | Perubahan |
|---|---|---|---|
| Total Titik Panas (VIIRS S-NPP nominal/tinggi) | 120.545 | 85.478 | -29,1% |
| Indeks Herfindahl-Hirschman (HHI) Provinsi | 0,2465 | 0,3736 | +51,6% (lebih terkonsentrasi) |
| Indeks Herfindahl-Hirschman (HHI) Kabupaten | 0,0617 | 0,1081 | +75,2% (lebih terkonsentrasi) |
| Pangsa Top 5 Kabupaten | 48,00% | 52,59% | +4,59% poin |
| Pangsa Provinsi Tertinggi (Sumatera Selatan) | 34,10% (41.102 titik) | 58,71% (50.187 titik) | +24,61% poin |

#### Tabel Sebaran Titik Panas per Provinsi (Januari–Oktober)
| Provinsi | 2019 (Jan–Okt) | Pangsa 2019 (%) | 2026 (Jan–Okt) | Pangsa 2026 (%) |
|---|---|---|---|---|
| SUMATERA SELATAN | 41.102 | 34,10% | 50.187 | 58,71% |
| KEPULAUAN BANGKA BELITUNG | 3.831 | 3,18% | 8.074 | 9,45% |
| JAMBI | 29.423 | 24,41% | 7.893 | 9,23% |
| RIAU | 30.913 | 25,64% | 6.050 | 7,08% |
| LAMPUNG | 6.093 | 5,05% | 5.815 | 6,80% |
| ACEH | 1.840 | 1,53% | 2.679 | 3,13% |
| SUMATERA UTARA | 1.807 | 1,50% | 1.428 | 1,67% |
| KEPULAUAN RIAU | 3.172 | 2,63% | 1.246 | 1,46% |
| SUMATERA BARAT | 1.536 | 1,27% | 1.235 | 1,44% |
| BENGKULU | 828 | 0,69% | 871 | 1,02% |
| **Total** | **120.545** | **100,00%** | **85.478** | **100,00%** |

---

### H2. Porsi Luas Terbakar: Gambut vs Mineral (Trase 2015–2024)

> **Status: Didukung**  
> *Kalimat temuan:* Luas kebakaran lahan di pesisir timur Sumatera (Riau dan Jambi) didominasi secara signifikan oleh lahan gambut (68%–78%), dan Sumatera Selatan mencatat luasan absolut gambut terbakar terbesar se-Sumatera (307.205 ha), sedangkan provinsi barat dan kepulauan didominasi kebakaran lahan mineral (>95%).

Sumber: Trase / MapBiomas Fire Collection 2 level kabupaten (2015–2024).

| Provinsi | Luas Terbakar Total (ha) | Gambut Terbakar (ha) | Mineral Terbakar (ha) | Porsi Gambut (%) |
|---|---|---|---|---|
| RIAU | 206.688,8 | 162.176,7 | 44.512,1 | **78,46%** |
| JAMBI | 85.123,9 | 58.120,7 | 27.003,2 | **68,28%** |
| SUMATERA BARAT | 31.448,1 | 17.091,7 | 14.356,4 | **54,35%** |
| SUMATERA SELATAN | 659.097,1 | 307.204,2 | 351.892,9 | **46,61%** |
| ACEH | 23.110,7 | 8.568,3 | 14.542,4 | **37,07%** |
| SUMATERA UTARA | 44.428,8 | 10.541,5 | 33.887,3 | **23,73%** |
| KEPULAUAN BANGKA BELITUNG | 61.832,2 | 2.812,0 | 59.020,2 | **4,55%** |
| LAMPUNG | 142.668,9 | 4.714,6 | 137.954,2 | **3,30%** |
| BENGKULU | 3.450,5 | 34,3 | 3.416,2 | **0,99%** |
| KEPULAUAN RIAU | 22.323,1 | 144,6 | 22.178,4 | **0,65%** |
| **Total Sumatera** | **1.280.172,1** | **571.408,5** | **708.763,6** | **44,64%** |

---

### H3. Respon Titik Panas terhadap ONI dan Anomali Curah Hujan

> **Status: Tidak konklusif**  
> *Kalimat temuan:* Pengujian korelasi titik panas terhadap anomali curah hujan dan fase ENSO (lag 0–3 bulan) dinyatakan tidak konklusif karena lapisan spasial curah hujan (CHIRPS) belum tersedia dalam pipeline hingga batas waktu 18 November 2026.

Catatan metode: Sesuai kesepakatan rencana kerja (tugas A8 & A9), kolom curah hujan dibiarkan bernilai `NaN` dan tidak diimputasi menggunakan estimasi sembarangan. ONI NOAA CPC tersedia dari DJF 1950 sampai ASO 2026 dan dipakai sebagai fitur model risiko S5; ini tidak menggantikan data hujan yang belum tersedia.

---

### H4. Konsentrasi Spasial Ekstrem Kabupaten (Distribusi Pareto)

> **Status: Didukung**  
> *Kalimat temuan:* Kejadian kebakaran di Sumatera terdistribusi secara sangat timpang, di mana hanya 8 dari 154 kabupaten (5,2%) menyumbang lebih dari separuh (50,6%) akumulasi titik panas sepanjang 2015–2026.

| Peringkat Kumulatif | Jumlah Kabupaten | Persentase Kabupaten | Kumulatif Titik Panas | Pangsa Kumulatif (%) |
|---|---|---|---|---|
| Top 1 (Ogan Komering Ilir) | 1 | 0,65% | 165.750 | 23,18% |
| Top 2 (+ Musi Banyuasin) | 2 | 1,30% | 225.640 | 31,55% |
| Ambang 50% Titik Panas | **8** | **5,19%** | **361.880** | **50,61%** |
| Top 10 Kabupaten | 10 | 6,49% | 392.905 | 54,94% |
| Top 20 Kabupaten | 20 | 12,99% | 493.093 | 68,95% |
| Ambang 80% Titik Panas | **33** | **21,43%** | **573.578** | **80,21%** |
| Sisa 121 Kabupaten | 121 | 78,57% | 141.523 | 19,79% |
| **Total Seluruh Kabupaten** | **154** | **100,00%** | **715.101** | **100,00%** |

#### 10 Kabupaten Teratas Penghasil Titik Panas (2015–2026)
1. **OGAN KOMERING ILIR** (Sumatera Selatan): 165.750 titik (23,18%)
2. **MUSI BANYUASIN** (Sumatera Selatan): 59.890 titik (8,38%)
3. **MUARO JAMBI** (Jambi): 32.149 titik (4,50%)
4. **TANJUNG JABUNG TIMUR** (Jambi): 22.924 titik (3,21%)
5. **ROKAN HILIR** (Riau): 22.053 titik (3,08%)
6. **PELALAWAN** (Riau): 21.492 titik (3,01%)
7. **BANYUASIN** (Sumatera Selatan): 20.311 titik (2,84%)
8. **INDRAGIRI HILIR** (Riau): 17.311 titik (2,42%)
9. **BENGKALIS** (Riau): 16.283 titik (2,28%)
10. **MUARA ENIM** (Sumatera Selatan): 14.742 titik (2,06%)

---

### H5. Kabupaten Kronis Karhutla

> **Status: Didukung**  
> *Definisi apriori $N$:* Suatu kabupaten ditetapkan sebagai **Kabupaten Kronis** jika kabupaten tersebut masuk dalam peringkat **Top 20 kabupaten dengan titik panas terbanyak di Sumatera selama minimal $N = 6$ tahun** dari 10 tahun pengamatan penuh (2015–2024).  
> *Kalimat temuan:* Teridentifikasi 11 kabupaten kronis yang persisten berada pada jajaran 20 kabupaten paling rawan karhutla selama sedikitnya 6 dari 10 tahun pengamatan, dengan Musi Banyuasin dan Musi Rawas tercatat selalu berada di jajaran teratas selama 9 tahun.

| No | Kabupaten | Provinsi | Frekuensi Masuk Top 20 ($N$) | Total Titik Panas (2015–2024) |
|---|---|---|---|---|
| 1 | MUSI BANYUASIN | SUMATERA SELATAN | **9 dari 10 tahun** | 50.810 |
| 2 | MUSI RAWAS | SUMATERA SELATAN | **9 dari 10 tahun** | 7.206 |
| 3 | ROKAN HILIR | RIAU | **8 dari 10 tahun** | 19.813 |
| 4 | INDRAGIRI HILIR | RIAU | **8 dari 10 tahun** | 15.908 |
| 5 | BANGKA SELATAN | KEPULAUAN BANGKA BELITUNG | **8 dari 10 tahun** | 8.611 |
| 6 | OGAN KOMERING ILIR | SUMATERA SELATAN | **7 dari 10 tahun** | 140.023 |
| 7 | PELALAWAN | RIAU | **7 dari 10 tahun** | 19.353 |
| 8 | BENGKALIS | RIAU | **7 dari 10 tahun** | 14.174 |
| 9 | MUARA ENIM | SUMATERA SELATAN | **7 dari 10 tahun** | 9.168 |
| 10 | BANGKA BARAT | KEPULAUAN BANGKA BELITUNG | **7 dari 10 tahun** | 2.622 |
| 11 | PESISIR SELATAN | SUMATERA BARAT | **6 dari 10 tahun** | 5.930 |

*(Catatan: Jika ambang batas diperluas menjadi $N \ge 5$ tahun, terdapat 6 kabupaten tambahan: Banyuasin, Muaro Jambi, Tanjung Jabung Timur, Rokan Hulu, Indragiri Hulu, dan Siak).*

---

### H6. Rezim Musiman Utara vs Selatan (Bimodal vs Unimodal)

> **Status: Didukung**  
> *Kalimat temuan:* Pola musiman kebakaran di Sumatera menunjukkan perbedaan rezim yang tegas antara wilayah utara/khatulistiwa yang bersifat bimodal (dua puncak di Feb–Mar dan Jul–Agt) versus wilayah selatan khatulistiwa yang bersifat unimodal ekstrem pada puncak kemarau monsun tenggara (Sep–Okt).

#### Proporsi Titik Panas Berdasarkan Bulan Kalender (%)
| Provinsi | Jan | Feb | Mar | Apr | Mei | Jun | Jul | Agu | Sep | Okt | Nov | Des | Rezim |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **ACEH** | 6,2% | **11,6%** | **12,8%** | 6,4% | 3,9% | 12,2% | **18,6%** | 13,2% | 5,1% | 7,4% | 1,4% | 1,2% | **Bimodal** |
| **SUMATERA UTARA** | 3,3% | **10,4%** | 9,0% | 4,9% | 4,9% | 15,2% | **22,7%** | 17,0% | 6,2% | 7,1% | 1,0% | 0,9% | **Bimodal** |
| **RIAU** | 1,9% | **8,4%** | **12,0%** | 4,2% | 1,3% | 3,6% | 16,4% | **24,7%** | **20,9%** | 6,0% | 0,4% | 0,3% | **Bimodal** |
| **KEPULAUAN RIAU** | 3,1% | **10,0%** | **27,2%** | 26,4% | 7,3% | 1,3% | 3,0% | 7,7% | 9,9% | 3,5% | 0,2% | 0,4% | **Puncak Awal** |
| **JAMBI** | 1,2% | 0,9% | 0,9% | 0,7% | 0,5% | 2,4% | 6,8% | 18,2% | **43,6%** | 21,6% | 1,7% | 1,4% | **Unimodal** |
| **SUMATERA SELATAN** | 0,3% | 0,2% | 0,3% | 0,3% | 0,4% | 1,1% | 2,8% | 9,2% | **36,1%** | **42,9%** | 4,5% | 1,9% | **Unimodal** |
| **LAMPUNG** | 0,6% | 0,4% | 0,5% | 0,8% | 0,7% | 2,8% | 5,7% | 13,9% | **29,4%** | **33,0%** | 8,9% | 3,3% | **Unimodal** |
| **BANGKA BELITUNG** | 1,2% | 1,8% | 1,5% | 0,9% | 0,8% | 2,3% | 8,4% | 22,7% | **33,5%** | 21,0% | 4,5% | 1,4% | **Unimodal** |

- **Wilayah Utara (Riau, Aceh, Sumut)** mengalami fenomena kemarau pertama akibat pengaruh ekuatorial dan monsun timur laut pada bulan Februari–Maret, disusul kemarau kedua di pertengahan tahun. Riau mencatat 20,4% titik panasnya terjadi pada Februari–Maret.
- **Wilayah Selatan (Sumsel, Lampung, Jambi)** sangat dipengaruhi monsun Australia/tenggara yang kering pada Agustus–Oktober. Di Sumatera Selatan, **79,0%** dari seluruh titik panas sepanjang 12 tahun terkonsentrasi hanya dalam 2 bulan (September dan Oktober), sementara di bulan Februari–Maret praktis mendekati nol (0,5%).

---

## Model risiko hotspot S5

Model HGB dipilih untuk horizon 1, 2, dan 3 bulan berdasarkan expanding rolling-origin folds 2015–2022 dan jendela validasi 2023–2024. Fitur hotspot memakai data bulan origin yang sudah selesai; pengamatan target tidak masuk ke fitur. Uji holdout mencakup target Januari 2025–Oktober 2026 (22 bulan × 154 kabupaten untuk tiap horizon). Ukurannya adalah Poisson deviance rata-rata atas hitungan hotspot; lebih rendah berarti prediksi lebih dekat menurut loss ini.

- **h=1:** deviance HGB 35,74; persistence 48,59; seasonal climatology 49,07; ENSO-conditioned climatology 38,54. HGB mengungguli ketiga pembanding pada holdout.
- **h=2:** HGB 42,37; persistence 113,41; seasonal climatology 48,94; ENSO-conditioned climatology 35,66. HGB mengungguli dua baseline wajib, tetapi tidak mengungguli ENSO-conditioned climatology.
- **h=3:** HGB 53,88; persistence 191,83; seasonal climatology 48,96; ENSO-conditioned climatology 37,87. HGB tidak mengungguli seasonal climatology maupun ENSO-conditioned climatology pada holdout.

Perbandingan di atas adalah point estimate dan bukan uji signifikansi. Test holdout tidak dipakai untuk memilih keluarga model; hasil horizon 3 tetap dilaporkan sebagai keterbatasan performa. Ekspor forecast menghasilkan 1.386 baris untuk 154 kabupaten, tiga target bulan (November 2026–Januari 2027), dan tiga skenario ONI bersyarat. Nilai skenario bukan prakiraan resmi CPC. `model_metrics.csv` dan `feature_importance.csv` belum dibuat karena kontrak kolomnya belum disepakati.
