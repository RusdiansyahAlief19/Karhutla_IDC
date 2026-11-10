# Hasil uji peta Looker Studio

**Status:** percobaan visual selesai; pengecekan cakupan sesudah mengganti CSV ke v2 perlu dikonfirmasi  
**Tanggal:** 10 November 2026  
**Report:** tempel tautan report dari Drive/Looker Studio setelah dipindah ke folder tim.

## Hasil

| Pertanyaan | Hasil yang terlihat | Kesimpulan |
|---|---|---|
| Apakah kode ISO provinsi dapat dipetakan? | Field `iso_3166_2` dikenali sebagai field geografis dan peta Google Maps menampilkan titik-titik provinsi Sumatra. | Kode dapat dipakai untuk menempatkan marker provinsi pada Google Maps. Uji ini belum menunjukkan batas provinsi terisi warna. |
| Apakah nama kabupaten/kota dapat dipetakan? | Field `geo_value` menampilkan kumpulan titik di sekitar Sumatra pada peta Google Maps. | Nama lokasi dapat dipakai untuk memplot marker. Belum dihitung berapa dari seluruh baris yang cocok tepat atau apakah semuanya jatuh di kabupaten yang benar. |
| Apa arti titik terpisah di timur laut? | Kemungkinan besar Kepulauan Anambas di Kepulauan Riau; wilayah itu memang terpisah jauh dari pulau utama Sumatra. | Cocokkan tooltip titik untuk memastikan namanya. Jangan menghapus Anambas hanya karena letaknya terpisah. |
| Bagaimana rencana visual kabupaten? | Peta titik/gelembung sudah dapat menampilkan lokasi kabupaten/kota. | Gunakan peta gelembung untuk rencana kabupaten apabila peta wilayah berisi (filled map) tidak tersedia atau pengenalan subdivisi tingkat kedua tidak konsisten. Ukuran gelembung nanti harus memakai metrik analisis yang nyata. |

## Catatan interpretasi

- Visual yang diuji adalah **Google Maps dengan marker/gelembung**, bukan choropleth yang mengisi seluruh poligon provinsi atau kabupaten dengan warna.
- `test_marker=1` hanya angka dummy agar chart mempunyai metrik. Legenda `test_marker` tidak menyampaikan tingkat kebakaran dan jangan dimasukkan ke temuan lomba.
- CSV v1 sempat memuat lima unit Banten karena pemilihan berdasarkan kotak geografis kasar. File pengganti [`looker_map_trial_data_sumatra_v2.csv`](looker_map_trial_data_sumatra_v2.csv) mengeluarkan Cilegon, Kota Serang, Lebak, Pandeglang, dan Serang.
- Sebelum menyatakan peta akhir bebas wilayah di luar cakupan, pastikan kedua chart memakai sumber CSV v2 dan periksa tooltip titik yang tampak jauh. Sampel ADM2 ini dibuat untuk uji visual dan bukan daftar batas final untuk analisis.
- Untuk hasil akhir dashboard, gunakan koordinat centroid dari dimensi kabupaten yang tervalidasi dan metrik kebakaran yang benar. Jangan memakai `test_marker`.

## File yang disimpan di repo

- [`looker_map_trial_data_sumatra_v2.csv`](looker_map_trial_data_sumatra_v2.csv) — data geografi uji.
- [`looker_map_trial.md`](looker_map_trial.md) — tujuan, cara uji, dan referensi.
- Dokumen ini — hasil sementara dan batas interpretasi.
