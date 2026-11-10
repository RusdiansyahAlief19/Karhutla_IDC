# Catatan percobaan Looker Studio: peta wilayah

**Status:** file uji siap; hasil visual di Looker Studio belum diverifikasi  
**Tanggal:** 10 November 2026  
**Tujuan:** menguji field peta secara terpisah dari dashboard lomba karhutla.

## Pertanyaan dan temuan awal

| Uji | Nilai/field yang dicoba | Temuan saat ini | Keputusan |
|---|---|---|---|
| Provinsi Sumatra | Kode ISO 3166-2: `ID-AC`, `ID-SU`, `ID-SB`, `ID-RI`, `ID-KR`, `ID-JA`, `ID-SS`, `ID-BE`, `ID-LA`, `ID-BB` | Kode sudah ada dalam kontrak data proyek. Belum dikonfirmasi sebagai kecocokan geografi pada peta Looker Studio. | Coba field bertipe **Country subdivision (1st level)** dan verifikasi semua 10 provinsi terwarnai. Jika kode tidak cocok, coba nama provinsi sebagai kontrol. |
| Kabupaten/kota | Nama dari `kab_name` | Bantuan resmi menyebut dukungan **Country subdivision (2nd level)**, tetapi tidak menjamin nama atau kode kabupaten/kota Indonesia dikenali. Kabupaten/kota juga tidak memakai kode ISO 3166-2 pada kolom kontrak ini; `kab_id` bersumber dari batas admin. | Status: belum teruji. Jika lokasi tidak dikenali atau ambigu, gunakan peta gelembung dari `latlon` centroid kabupaten/kota. |

## Cara menjalankan uji terpisah

1. Buat **laporan Looker Studio baru** bernama `Uji peta wilayah karhutla — terpisah`; jangan menambahkan komponen atau mengubah dashboard lomba.
2. Unggah file versi terbaru [`looker_map_trial_data_sumatra_v2.csv`](looker_map_trial_data_sumatra_v2.csv) lewat **CSV File Upload**. File ini memuat 10 baris provinsi dengan kode ISO dan 152 nama unit ADM2 di sekitar Sumatra berdasarkan batas lokal. Lima unit Banten yang sempat ikut tertangkap oleh kotak geografis kasar sudah dikeluarkan: Cilegon, Kota Serang, Lebak, Pandeglang, dan Serang. Koordinat `latlon` adalah centroid geometri ADM2. `test_marker=1` hanyalah penanda agar visual peta dapat dirender; ini bukan data hotspot atau hasil analisis. Tetap periksa nama/titik wilayah pada peta sebelum menafsirkan hasil.
3. Untuk uji provinsi, tambahkan peta Google Maps dengan dimensi geografis **Country subdivision (1st level)** memakai `iso_3166_2`; filter `level` = `province`. Periksa apakah semua 10 provinsi terpetakan di Sumatra.
4. Untuk uji kabupaten/kota, tambahkan peta kedua dengan **Country subdivision (2nd level)** memakai `geo_value`; filter `level` = `kabupaten_kota`. Catat jumlah lokasi yang dikenali dan nilai yang gagal atau ambigu.
5. Bila peta tingkat kedua gagal, ubah visual kabupaten menjadi peta gelembung berbasis koordinat `latlon` (format `lat,lon`). Untuk uji ini, `latlon` berasal dari centroid geometri ADM2; dalam dashboard akhir, ukuran gelembung harus memakai metrik yang benar-benar tersedia. Jangan menyamakan jumlah hotspot dengan luas terbakar.
6. Catat status setiap visual, jumlah wilayah yang berhasil dipetakan, contoh nilai gagal, serta tangkapan layar sebelum memutuskan visual dashboard lomba.

## Batas kesimpulan

Dokumentasi Google menyatakan Google Maps di Looker Studio mendukung subdivisi negara tingkat kedua, misalnya county di Amerika Serikat serta subdivisi tingkat kedua di negara lain. Pernyataan itu bukan bukti bahwa nama/kode administratif Indonesia akan dikenali otomatis. Karena halaman laporan Looker Studio tidak tersedia untuk diuji di sesi ini, kedua hasil uji tetap **belum diverifikasi langsung**.

## Referensi

- [Looker Studio Help — catatan dukungan subdivisi negara tingkat kedua](https://support.google.com/looker-studio/answer/10331528?hl=id)
- Kontrak field geografis lokal: [`docs/data_dictionary.md`](data_dictionary.md) (`iso_3166_2`, `kab_id`, `kab_name`, `latlon`).
- Geometri ADM2 untuk file uji: geoBoundaries Indonesia ADM2, boundary year 2020, metadata dan lisensi dicatat di `data/raw/boundaries/gbOpen_IDN_ADM2.json`.
