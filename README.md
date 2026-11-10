# karhutla-idc

Pipeline data untuk dashboard Looker Studio, lomba IDC Dateraquest 2.0, subtema Preservasi Ekosistem Tropis. Topiknya karhutla Sumatera 2015–2026. Dashboard tidak dibuat di repo ini.

## Perintah

Di mesin ini `make` belum terpasang. Perintah yang setara:

```text
python -m src.ingest.oni
python -m src.ingest.boundaries
python -m pytest
```

Jika `make` tersedia, targetnya `make ingest`, `make check`, `make build`, `make model`, dan `make export`. Tiga target terakhir belum diisi dan sengaja berhenti.

`python -m src.ingest.oni` dan `python -m src.ingest.boundaries` hanya mengunduh URL di handover. Kalau URL gagal, skrip berhenti. Tidak ada sumber pengganti.

Berkas di `data/raw` tidak ditimpa. Unduhan ulang yang isinya sama dibiarkan. Isi yang berbeda menghentikan skrip. Checksum SHA-256 ditulis di `data/raw/SHA256SUMS`.

## Lingkungan

Target proyek Python 3.11. Mesin yang dipakai saat S0 hanya memiliki Python 3.10.11, jadi paket belum diinstal lewat `pip install -e .` (syarat `requires-python` menolaknya). Tes S0 dijalankan dengan Python yang ada setelah `pandera` dan `pytest` terpasang.

## Unduhan S0

Berkas mentah tidak ikut ke Git karena ukurannya besar. Yang di-commit hanya `data/raw/SHA256SUMS`. Di mesin yang sudah menjalankan skrip, berkasnya:

- `data/raw/oni/oni.ascii.txt` — DJF 1950 sampai ASO 2026.
- `data/raw/boundaries/gbOpen_IDN_ADM2.json` dan `idn_adm2.geojson` — 519 kabupaten/kota se-Indonesia, tahun batas 2020.

## Yang belum masuk pipeline

- Arsip FIRMS (perlu login atau kode email, hasilnya lewat email).
- Berkas Trase (tombol unduh di situs).
- SiPongi, CHIRPS, peta gambut, penduduk BPS, OpenAQ.
