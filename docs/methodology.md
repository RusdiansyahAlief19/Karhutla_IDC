# Metodologi — draf untuk naskah

Status: draf berdasarkan panel interim dan temuan pada repo utama commit `ca73ef9` (18 November 2026). Katalog URL, versi, kolom, dan lisensi sumber dicatat terpisah di [sources.md](sources.md).

## Cakupan dan satuan analisis

Analisis mencakup 10 provinsi Sumatera. Deret hotspot bulanan dimulai Januari 2015 dan berakhir pada 31 Oktober 2026. Satuan observasinya adalah deteksi hotspot; hitungan ini tidak dinyatakan sebagai luas terbakar. Metrik burned area dan burned peat dari Trase dinyatakan dalam hektare dan tersedia secara tahunan untuk 2015–2024.

## Data dan penyaringan

Deteksi aktif api berasal dari VIIRS S-NPP 375 m Collection 2 pada FIRMS. Arsip standar digunakan hingga Juli 2026 dan data near real-time (NRT) untuk Agustus–Oktober 2026. Baris dipilih untuk satelit `SNPP` dan confidence nominal atau tinggi (`n`/`h`). Pada arsip yang memiliki kolom `type`, hanya `type=0` yang dipakai. Berkas NRT tidak memiliki kolom `type`, sehingga filter tersebut tidak dapat diterapkan pada NRT; perbedaan ini dicatat sebagai keterbatasan.

Batas kabupaten/kota berasal dari geoBoundaries ADM2 tahun 2020. Crosswalk final menghubungkan 154 kabupaten/kota di Sumatera ke `shapeID`: 143 padanan nama persis dan 11 padanan yang telah ditinjau manual. Data Trase terdiri dari dua metrik tahunan, burned area total dan burned peatlands. Luas mineral dihitung sebagai total dikurangi luas gambut; rasio gambut dihitung terhadap total luas terbakar pada kabupaten-tahun yang sama.

## Spatial join dan panel

Koordinat FIRMS diuji terhadap poligon ADM2. Penyaringan bounding box memperkecil kandidat poligon sebelum pemeriksaan point-in-polygon. Hasil join dan jumlah titik yang tidak terpasangkan dicatat pada log audit. Dari 836.483 deteksi yang lolos filter sumber, 715.101 masuk tepat ke satu dari 154 kabupaten Sumatera, 121.382 tidak masuk poligon kabupaten Sumatera, dan tidak ada titik dengan lebih dari satu padanan.

Panel hotspot bulanan memuat 142 bulan × 154 kabupaten (21.868 baris). Bulan-kabupaten tanpa deteksi diisi nol untuk hitungan hotspot, deteksi high-confidence, FRP, dan hari terbakar. Label `data_quality` membedakan sumber arsip standar (`SP`) dan NRT. Panel Trase tahunan memuat 10 tahun × 154 kabupaten (1.540 baris). Nilai luas Trase tetap tahunan dan tidak ditempelkan sebagai nilai bulanan.

Area kabupaten dan centroid dihitung dari geometri batas dalam WGS84 / Equal Area Cylindrical (EPSG:6933), bukan dari derajat lintang/bujur. Data proporsi tutupan gambut belum ada. `peat_share_pct`, curah hujan, dan penduduk tetap `NaN`; porsi tahunan hektare terbakar di gambut (`peat_burn_share_pct`) tidak dipakai sebagai penggantinya.

## Rancangan analisis

- **H1 — Konsentrasi 2026 dan 2019:** membandingkan Januari–Oktober pada kedua tahun. HHI dihitung dari pangsa deteksi tiap wilayah (jumlah kuadrat pangsa). Temuan tidak mendukung dugaan bahwa 2026 lebih menyebar: total deteksi lebih rendah, sementara HHI kabupaten lebih tinggi dan pangsa Sumatera Selatan meningkat.
- **H2 — Gambut dan mineral:** membandingkan luas tahunan terbakar di gambut dan mineral menurut provinsi menggunakan Trase 2015–2024.
- **H3 — Hujan dan ONI:** menguji hubungan titik panas dengan anomali hujan dan ONI pada jeda 0–3 bulan. CHIRPS belum tersedia pada cut-off 18 November 2026; nilai hujan tetap `NaN`, sehingga hasil hipotesis ini tidak konklusif.
- **H4 — Konsentrasi Pareto:** mengurutkan kabupaten berdasarkan akumulasi deteksi hotspot, lalu menghitung jumlah dan pangsa kumulatif sampai melewati 50% dan 80%.
- **H5 — Kabupaten kronis:** sebelum melihat hasil, kabupaten didefinisikan kronis bila masuk Top 20 hotspot sedikitnya 6 dari 10 tahun penuh 2015–2024.
- **H6 — Pola musiman:** membandingkan distribusi deteksi menurut bulan kalender antarprovinsi. Istilah bimodal dan unimodal merangkum jumlah puncak yang tampak pada distribusi tersebut.

## Model risiko hotspot S5

Model memprediksi **jumlah deteksi hotspot** pada satu, dua, dan tiga bulan ke depan (`h=1,2,3`). Semua fitur hotspot, tetangga, dan provinsi memakai data sampai bulan origin yang sudah selesai. `hs_lag1` adalah hitungan pada bulan origin; hitungan target tidak masuk ke fitur. ONI CPC dipetakan dari musim tiga-bulanan ke bulan tengahnya; fitur ONI terakhir memakai nilai yang berpusat pada `t-1`, sehingga jendela tiga bulannya berakhir pada origin `t`. Nilai `NDJ Y` dipetakan ke Desember tahun `Y`.

Hitungan target dinormalisasi menjadi laju per luas kabupaten untuk pelatihan HGB Poisson dan Poisson GLM, dengan luas kabupaten sebagai exposure; prediksi dikembalikan ke jumlah hitungan. Skor evaluasi tetap membandingkan hitungan, bukan hektare. GLM mengisi nilai fitur hilang menggunakan median dari baris training saja; HGB menerima nilai hilang secara langsung. Peat share tidak menjadi fitur karena sumber tutupan gambut belum tersedia.

Validasi memakai expanding rolling-origin dengan sedikitnya 24 bulan label training dan blok validasi enam bulan pada target 2015–2022. Untuk tiap horizon, label training berakhir pada origin pertama di blok validasi agar tidak memakai target yang belum tersedia saat prediksi pertama. Seleksi juga memakai jendela validasi Januari 2023–Desember 2024, dengan cutoff label disesuaikan ke origin pertama per horizon. Test terpisah mencakup target Januari 2025–Oktober 2026; model test dilatih hanya sampai origin pertama untuk tiap horizon (Desember 2024 untuk h=1, November 2024 untuk h=2, dan Oktober 2024 untuk h=3). Fitur hotspot kemudian mengikuti observasi origin yang sudah selesai. HGB dan GLM dibandingkan dengan persistence (hitungan origin) dan seasonal climatology kabupaten-bulan; ENSO-conditioned climatology juga dihitung sebagai pembanding tambahan. Kandidat dipilih hanya jika mengungguli dua baseline wajib pada rolling-origin dan jendela validasi. Test dilaporkan sebagai pemeriksaan holdout dan tidak dipakai untuk memilih keluarga model. Setelah evaluasi selesai, kandidat dilatih ulang menggunakan seluruh label yang tersedia sampai Oktober 2026 untuk proyeksi setelah cutoff.

Pada test holdout, Poisson deviance rata-rata HGB untuk h=1 adalah 35,74, dibanding persistence 48,59, seasonal climatology 49,07, dan ENSO-conditioned climatology 38,54. Untuk h=2, HGB 42,37 lebih baik daripada persistence 113,41 dan seasonal climatology 48,94, tetapi lebih buruk daripada ENSO-conditioned climatology 35,66. Untuk h=3, HGB 53,88 tidak mengungguli seasonal climatology 48,96 atau ENSO-conditioned climatology 37,87. Nilai deviance yang lebih rendah lebih baik; ini perbandingan titik dan bukan uji signifikansi. Karena test tidak dipakai untuk seleksi, kegagalan h=3 tetap dicatat dan tidak mengubah pemilihan model.

Risiko untuk origin 31 Oktober 2026 diproyeksikan pada November 2026, Desember 2026, dan Januari 2027. Skenario `netral`, `el_nino`, dan `la_nina` menetapkan nilai ONI bersyarat 0.0, +1.5, dan -1.0. Nilai ini adalah asumsi skenario, bukan prakiraan CPC. Untuk monitoring dan prakiraan ENSO resminya, CPC menggunakan RONI sejak 1 Februari 2026; output proyek berbasis ONI harus disebut sebagai indikator historis ONI, bukan status resmi CPC 2026.

`risk_score` menormalkan `log1p(hotspot per 100 km²)` dengan maksimum yang diamati pada training 2015–2022, lalu memotong skornya ke rentang 0–1. Batas kelas risiko adalah persentil 50, 75, dan 90 dari laju hotspot positif pada periode training tersebut. Ini ukuran relatif terhadap sebaran historis training. Kolom driver per kabupaten hanya diisi untuk GLM melalui kontribusi fitur terstandar; HGB dan baseline tidak memberi atribusi yang disediakan pipeline, sehingga kolom driver-nya kosong. Kontribusi fitur bukan penjelasan kausal.

Ekspor Looker yang memiliki kontrak pada handover divalidasi dengan Pandera sebelum ditulis. `model_metrics.csv` dan `feature_importance.csv` tidak ditulis sampai daftar kolom disepakati. `concentration_index` juga tetap `NaN` karena rumusnya belum dikunci.

## Batas interpretasi

Hasil menggambarkan deteksi hotspot dan luasan terbakar dari sumber yang berbeda. Keduanya dilaporkan terpisah. Keterbatasan utama meliputi cakupan Trase yang aktualnya hanya 2015–2024, tidak tersedianya lapisan CHIRPS pada tanggal cut-off, ketiadaan kolom `type` pada NRT, serta deteksi FIRMS yang tidak jatuh pada poligon kabupaten Sumatera. Temuan ditulis sebagai pola atau keterkaitan; hasil ini tidak menetapkan sebab-akibat.
