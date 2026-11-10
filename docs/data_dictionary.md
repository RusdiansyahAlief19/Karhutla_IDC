# Kamus data

Kolom di bawah ini menyalin kontrak bagian 6 handover. Arti yang tidak tertulis di sana dikosongkan. `model_metrics.csv` dan `feature_importance.csv` disebut sebagai berkas keluaran, tetapi daftar kolomnya belum ada, jadi tidak dibuat di sini.

Sel kosong pada data asli tetap `NaN`. Tidak ada imputasi.

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
| peat_share_pct | |
| population_latest | Boleh kosong |
| population_year | Boleh kosong |

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
| rain_mm | |
| rain_anom_mm | |
| rain_anom_pct | |
| oni | |
| enso_phase | Nilai kategori belum dikunci |
| data_quality | `SP` atau `NRT` |
| prov_name | Turunan dari dimensi |
| kab_name | Turunan dari dimensi |
| latlon | Turunan dari dimensi |
| peat_share_pct | Turunan dari dimensi |

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
| peat_share_pct | Turunan |

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
| concentration_index | Rumus belum dikunci. Hipotesis H1 menyebut Herfindahl atau share provinsi teratas sebagai contoh, bukan keputusan akhir. |

## ml_risk_forecast.csv

| Kolom | Keterangan dari brief |
|---|---|
| kab_id | |
| kab_name | |
| prov_name | |
| target_window | Contoh di brief: `2027-06_2027-10` |
| scenario | `netral`, `el_nino`, `la_nina` |
| risk_score | 0 sampai 1 |
| risk_rank | |
| risk_class | `rendah`, `sedang`, `tinggi`, `sangat_tinggi` |
| top_driver_1 | |
| top_driver_2 | |
| latlon | |

## model_metrics.csv

Daftar kolom belum ditentukan di bagian 6.

## feature_importance.csv

Daftar kolom belum ditentukan di bagian 6.
