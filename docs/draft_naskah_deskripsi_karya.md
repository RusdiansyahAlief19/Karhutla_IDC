# Draf Naskah: Deskripsi Karya dan Data & Metode

Status: draf kerja per 18 November 2026. Angka dan status hipotesis merujuk pada `docs/findings.md`; rincian sumber merujuk pada `docs/sources.md`. Judul dan susunan halaman masih dapat disesuaikan dengan format lomba.

## 1. Deskripsi Karya

### Judul kerja

**Karhutla Sumatera dalam Ruang dan Waktu: Hotspot, Konsentrasi Wilayah, dan Luas Terbakar 2015–2026**

### Naskah deskripsi

Karya ini dirancang sebagai dashboard interaktif untuk membantu pengguna mengeksplorasi pola kebakaran hutan dan lahan di 10 provinsi Sumatera. Dashboard menggabungkan peta dan deret waktu deteksi hotspot VIIRS S-NPP dengan ringkasan tahunan luas terbakar dan luas terbakar di gambut dari Trase. Rentang data hotspot bulanan adalah Januari 2015–Oktober 2026, sementara metrik luas terbakar Trase yang tersedia mencakup 2015–2024.

Tampilan dirancang untuk membantu pengguna melihat kapan dan di kabupaten mana deteksi hotspot terkonsentrasi, membandingkan pola musiman antarprovinsi, serta membaca porsi luas terbakar gambut dan mineral pada tingkat tahunan. Hitungan hotspot dan luas terbakar ditampilkan sebagai ukuran yang berbeda: satuan hotspot adalah jumlah deteksi, sedangkan luas terbakar menggunakan hektare. Luas tahunan Trase tidak disebarkan ke nilai bulanan.

Analisis menunjukkan konsentrasi hotspot yang timpang: delapan dari 154 kabupaten menyumbang 50,6% deteksi pada periode analisis, dan Ogan Komering Ilir menyumbang 23,2%. Perbandingan Januari–Oktober 2026 dengan periode yang sama pada 2019 tidak mendukung dugaan bahwa hotspot makin menyebar. Total deteksi 2026 lebih rendah, sementara HHI tingkat kabupaten meningkat dan pangsa Sumatera Selatan bertambah. Analisis Trase menunjukkan bagian luas terbakar di gambut yang tinggi di Riau dan Jambi; hasil musiman juga memperlihatkan puncak yang berbeda antara sejumlah provinsi utara/khatulistiwa dan selatan.

Temuan hujan dan ONI dinyatakan tidak konklusif karena data spasial hujan CHIRPS belum tersedia pada cut-off analisis. Dashboard dan naskah tidak mengatribusikan sebab-akibat pada pola yang terlihat. Rancangan akhir mengikuti batas maksimum tiga halaman dashboard; susunan halaman dan komponen visual perlu diselaraskan dengan implementasi Looker Studio tim.

## 2. Data & Metode

### 2.1 Wilayah, periode, dan unit analisis

Wilayah analisis mencakup 10 provinsi Sumatera dan 154 kabupaten/kota. Panel hotspot bulanan dimulai Januari 2015 dan berakhir 31 Oktober 2026. Data luas terbakar dan luas terbakar gambut Trase digunakan pada unit kabupaten-tahun untuk 2015–2024. Karena resolusi waktunya berbeda, metrik Trase dipertahankan tahunan.

### 2.2 Sumber dan variabel

| Sumber | Periode dan unit | Penggunaan |
|---|---|---|
| NASA FIRMS, VIIRS S-NPP 375 m Collection 2 | Deteksi hotspot, Januari 2015–31 Oktober 2026 | Koordinat, tanggal akuisisi, satelit, confidence, FRP, dan `type` jika tersedia |
| geoBoundaries ADM2, batas tahun 2020 | Poligon 519 unit ADM2 nasional | Geometri untuk spatial join; 154 unit Sumatera dipilih melalui crosswalk final |
| Trase / MapBiomas Indonesia Fire Collection 2 | Burned area tahunan, 2015–2024 | Luas terbakar total per kabupaten-tahun |
| Trase — Fire on peatlands | Burned peatlands tahunan, 2015–2024 | Luas terbakar gambut per kabupaten-tahun |
| NOAA CPC ONI | Indeks ENSO bulanan | Konteks ENSO; belum cukup untuk menyimpulkan H3 tanpa data hujan |
| CHIRPS | Tidak tersedia pada cut-off 18 November 2026 | Kolom hujan dan anomali hujan dipertahankan sebagai `NaN` |

URL, versi, tanggal akses, lisensi, dan catatan keterbatasan sumber tersedia di `docs/sources.md`.

### 2.3 Filter dan spatial join

Data FIRMS dibatasi pada VIIRS S-NPP (`satellite=SNPP`) dengan confidence nominal atau tinggi (`n`/`h`). Pada arsip yang memiliki kolom `type`, hanya deteksi `type=0` yang disertakan. Data NRT tidak memiliki kolom `type`, sehingga filter itu tidak dapat diterapkan pada periode NRT Agustus–Oktober 2026; perbedaan cakupan filter ini menjadi keterbatasan data.

Crosswalk final memasangkan 143 nama Trase dengan nama batas yang sama dan 11 nama yang telah ditinjau manual. Koordinat diuji terhadap poligon kabupaten menggunakan penyaringan bounding box dan pemeriksaan point-in-polygon. Dari 836.483 deteksi yang lolos filter sumber, 715.101 dipasangkan ke tepat satu kabupaten Sumatera; 121.382 berada di luar poligon kabupaten Sumatera dan nol titik memperoleh lebih dari satu padanan. Jumlah yang tidak masuk poligon dicatat pada log audit.

### 2.4 Pembentukan panel

Panel bulanan berisi 142 bulan × 154 kabupaten, atau 21.868 baris. Kabupaten-bulan tanpa deteksi diisi nol untuk hitungan hotspot, hitungan high-confidence, FRP, dan hari terbakar. Label kualitas data membedakan arsip standar (`SP`) dan NRT. Nilai hujan yang tidak tersedia tetap `NaN` dan tidak diisi dengan estimasi.

Panel tahunan berisi 1.540 baris kabupaten-tahun (154 kabupaten × 10 tahun, 2015–2024). Burned area mineral dihitung dari burned area total dikurangi burned peatlands; porsi gambut dihitung dari luas terbakar gambut dibagi luas terbakar total pada unit kabupaten-tahun yang sama. Hitungan hotspot tahunan merupakan agregasi dari deteksi bulanan yang telah terpasangkan.

### 2.5 Rancangan analisis

- **H1 — Konsentrasi 2026 dibanding 2019:** membandingkan Januari–Oktober pada kedua tahun. HHI dihitung sebagai jumlah kuadrat pangsa tiap unit wilayah. Hasil tidak mendukung hipotesis sebaran 2026 yang lebih luas; HHI kabupaten naik 75,2% dan pangsa Sumatera Selatan meningkat dari 34,1% menjadi 58,7%.
- **H2 — Gambut dan mineral:** membandingkan luasan tahunan Trase 2015–2024. Porsi gambut tercatat 78,5% di Riau dan 68,3% di Jambi; Sumatera Selatan memiliki luas terbakar gambut mutlak terbesar, 307.205 ha.
- **H3 — Hujan dan ONI:** rancangan menguji hubungan dengan jeda 0–3 bulan. Karena CHIRPS belum tersedia, hasil dinyatakan tidak konklusif dan nilai hujan tidak diimputasi.
- **H4 — Konsentrasi kabupaten:** mengurutkan kabupaten menurut akumulasi deteksi dan menghitung pangsa kumulatif. Delapan kabupaten (5,2%) menyumbang 50,6% deteksi; Ogan Komering Ilir menyumbang 23,2%.
- **H5 — Kabupaten kronis:** definisi ditetapkan sebelum membaca hasil: kabupaten yang masuk Top 20 hotspot sedikitnya enam dari sepuluh tahun penuh 2015–2024. Dengan ambang ini ditemukan 11 kabupaten.
- **H6 — Musiman utara dan selatan:** membandingkan distribusi deteksi menurut bulan kalender antarprovinsi. Pola yang tercatat cenderung bimodal di Aceh, Sumatera Utara, dan Riau, serta unimodal di Jambi, Sumatera Selatan, dan Lampung. Di Sumatera Selatan, 79,0% deteksi terjadi pada September–Oktober.

### 2.6 Batas interpretasi

FIRMS mengukur deteksi hotspot, sedangkan Trase melaporkan luas terbakar dalam hektare. Hasil keduanya tidak dijumlahkan atau diperlakukan sebagai metrik yang sama. Trase hanya tersedia sampai 2024, NRT tidak menyediakan `type`, CHIRPS belum tersedia, dan 121.382 deteksi tidak jatuh pada poligon kabupaten Sumatera yang digunakan. Temuan menggambarkan pola dan keterkaitan pada data yang tersedia; temuan tidak menetapkan sebab-akibat.
