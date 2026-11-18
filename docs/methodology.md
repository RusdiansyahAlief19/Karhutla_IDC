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

## Rancangan analisis

- **H1 — Konsentrasi 2026 dan 2019:** membandingkan Januari–Oktober pada kedua tahun. HHI dihitung dari pangsa deteksi tiap wilayah (jumlah kuadrat pangsa). Temuan tidak mendukung dugaan bahwa 2026 lebih menyebar: total deteksi lebih rendah, sementara HHI kabupaten lebih tinggi dan pangsa Sumatera Selatan meningkat.
- **H2 — Gambut dan mineral:** membandingkan luas tahunan terbakar di gambut dan mineral menurut provinsi menggunakan Trase 2015–2024.
- **H3 — Hujan dan ONI:** menguji hubungan titik panas dengan anomali hujan dan ONI pada jeda 0–3 bulan. CHIRPS belum tersedia pada cut-off 18 November 2026; nilai hujan tetap `NaN`, sehingga hasil hipotesis ini tidak konklusif.
- **H4 — Konsentrasi Pareto:** mengurutkan kabupaten berdasarkan akumulasi deteksi hotspot, lalu menghitung jumlah dan pangsa kumulatif sampai melewati 50% dan 80%.
- **H5 — Kabupaten kronis:** sebelum melihat hasil, kabupaten didefinisikan kronis bila masuk Top 20 hotspot sedikitnya 6 dari 10 tahun penuh 2015–2024.
- **H6 — Pola musiman:** membandingkan distribusi deteksi menurut bulan kalender antarprovinsi. Istilah bimodal dan unimodal merangkum jumlah puncak yang tampak pada distribusi tersebut.

## Batas interpretasi

Hasil menggambarkan deteksi hotspot dan luasan terbakar dari sumber yang berbeda. Keduanya dilaporkan terpisah. Keterbatasan utama meliputi cakupan Trase yang aktualnya hanya 2015–2024, tidak tersedianya lapisan CHIRPS pada tanggal cut-off, ketiadaan kolom `type` pada NRT, serta deteksi FIRMS yang tidak jatuh pada poligon kabupaten Sumatera. Temuan ditulis sebagai pola atau keterkaitan; hasil ini tidak menetapkan sebab-akibat.
