# Kamus data

Kolom di bawah ini menyalin kontrak bagian 6 handover. Arti yang tidak tertulis di sana dikosongkan. `model_metrics.csv` dan `feature_importance.csv` disebut sebagai berkas keluaran, tetapi daftar kolomnya belum ada, jadi tidak dibuat di sini.

Sel kosong pada data asli tetap `NaN`. Tidak ada imputasi.

`peat_share_pct` berarti proporsi area kabupaten yang berupa gambut. Dataset
tersebut belum tersedia, sehingga kolom ini tetap `NaN`. `peat_burn_share_pct`
berarti proporsi hektare terbakar yang berada di gambut; nilainya tidak dipakai
sebagai pengganti proporsi lahan.

## dim_kabupaten.csv

Satu baris per kabupaten atau kota.

| Kolom | Keterangan dari brief |
|---|---|
| kab_id | |
| kab_name | |
| prov_id | |
| prov_name | |
| iso_3166_2 | ID-AC, ID-SU, ID-SB, ID-RI, ID-KR, ID-JA, ID-SS, ID-BE, ID-LA, ID-BB |
| centroid_lat | |
| centroid_lon | |
| latlon | String `"lat,lon"` untuk field geografis Looker |
| area_km2 | Dihitung pada CRS equal-area, bukan dari derajat |
| peat_share_pct | Proporsi area kabupaten yang berupa gambut; `NaN` sampai raster tersedia |
| population_latest | `NaN`; data penduduk BPS belum diingest |
| population_year | `NaN`; data penduduk BPS belum diingest |

## fact_kab_month.csv

Satu baris per kabupaten per bulan, 2015-01 sampai cut-off.

| Kolom | Keterangan dari brief |
|---|---|
| month | `YYYY-MM-01` |
| kab_id | |
| hotspot_count | Bukan luas terbakar |
| hotspot_high_conf | |
| hotspot_per_100km2 | |
| frp_sum | |
| burn_days | |
| rain_mm | `NaN`; CHIRPS belum diingest |
| rain_anom_mm | `NaN`; CHIRPS belum diingest |
| rain_anom_pct | `NaN`; CHIRPS belum diingest |
| oni | |
| enso_phase | `el_nino`, `la_nina`, atau `netral` dari ONI; `NaN` jika ONI tidak tersedia |
| data_quality | `SP` atau `NRT` |
| prov_name | Turunan dari dimensi |
| kab_name | Turunan dari dimensi |
| latlon | Turunan dari dimensi |
| peat_share_pct | Proporsi area kabupaten yang berupa gambut; `NaN` sampai raster tersedia |

## fact_kab_year.csv

Satu baris per kabupaten per tahun. Kolom turunan mengikuti daftar yang sama dengan tabel bulan.

| Kolom | Keterangan dari brief |
|---|---|
| year | |
| kab_id | |
| burned_ha_total | Bukan jumlah hotspot |
| burned_ha_peat | |
| burned_ha_mineral | |
| peat_burn_share_pct | |
| hotspot_count_year | |
| source | |
| notes | |
| prov_name | Turunan |
| kab_name | Turunan |
| latlon | Turunan |
| peat_share_pct | Proporsi area kabupaten yang berupa gambut; `NaN` sampai raster tersedia |

## prov_summary_year.csv

| Kolom | Keterangan dari brief |
|---|---|
| year | |
| prov_name | |
| iso_3166_2 | |
| hotspot_count | |
| burned_ha_total | |
| burned_ha_peat | |
| share_of_sumatra_hotspot_pct | |
| concentration_index | `NaN` sampai tim menyepakati rumus. HHI dan pangsa provinsi teratas adalah pilihan berbeda. |

## ml_risk_forecast.csv

| Kolom | Keterangan dari brief |
|---|---|
| kab_id | |
| kab_name | |
| prov_name | |
| target_window | Bulan target `YYYY-MM`; untuk origin Oktober 2026, keluaran mencakup November 2026, Desember 2026, dan Januari 2027 |
| scenario | Skenario ONI bersyarat: 0.0, +1.5, -1.0; bukan prakiraan resmi CPC |
| risk_score | 0 sampai 1 |
| risk_rank | |
| risk_class | `rendah`, `sedang`, `tinggi`, `sangat_tinggi` |
| top_driver_1 | Grup kontribusi fitur terbesar dari GLM; kosong untuk HGB/baseline, bukan sebab-akibat |
| top_driver_2 | Grup kontribusi fitur terbesar kedua dari GLM; kosong untuk HGB/baseline, bukan sebab-akibat |
| latlon | |

## model_metrics.csv

Daftar kolom belum ditentukan di bagian 6.

## feature_importance.csv

Daftar kolom belum ditentukan di bagian 6.

Kedua berkas model ini tidak ditulis sampai kontrak kolom ditentukan. Kolom
forecast yang nullable tetap kosong jika keluarga terpilih bukan GLM. Berkas
`data/processed/model_metrics.csv` yang mungkin sudah ada lokal berasal dari
run lama dan tidak diperbarui oleh pipeline saat ini.
