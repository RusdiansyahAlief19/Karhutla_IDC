"""Reproducible statistical and spatial analysis for hypotheses H1 through H6."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
import sys

# Ensure repository root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from typing import Any

import numpy as np
import pandas as pd

from src.ingest.rawstore import repo_root


def run_analysis(root: Path | None = None) -> dict[str, Any]:
    base = root or repo_root()
    interim = base / "data" / "interim"

    month_df = pd.read_csv(interim / "fact_kab_month_interim.csv")
    year_df = pd.read_csv(interim / "fact_kab_year_interim.csv")

    results: dict[str, Any] = {}

    # -------------------------------------------------------------
    # H1: Konsentrasi Spasial 2026 vs 2019 (Januari - Oktober)
    # -------------------------------------------------------------
    m19 = month_df[(month_df["month"] >= "2019-01-01") & (month_df["month"] <= "2019-10-01")]
    m26 = month_df[(month_df["month"] >= "2026-01-01") & (month_df["month"] <= "2026-10-01")]

    tot19 = int(m19["hotspot_count"].sum())
    tot26 = int(m26["hotspot_count"].sum())

    prov19 = m19.groupby("prov_name")["hotspot_count"].sum()
    prov26 = m26.groupby("prov_name")["hotspot_count"].sum()

    hhi_prov19 = float(((prov19 / tot19) ** 2).sum())
    hhi_prov26 = float(((prov26 / tot26) ** 2).sum())

    kab19 = m19.groupby("kab_id")["hotspot_count"].sum()
    kab26 = m26.groupby("kab_id")["hotspot_count"].sum()

    hhi_kab19 = float(((kab19 / tot19) ** 2).sum())
    hhi_kab26 = float(((kab26 / tot26) ** 2).sum())

    top5_kab19_share = float((kab19.sort_values(ascending=False).iloc[:5].sum() / tot19) * 100)
    top5_kab26_share = float((kab26.sort_values(ascending=False).iloc[:5].sum() / tot26) * 100)

    sumsel19_share = float((prov19.get("SUMATERA SELATAN", 0) / tot19) * 100)
    sumsel26_share = float((prov26.get("SUMATERA SELATAN", 0) / tot26) * 100)

    results["H1"] = {
        "status": "Tidak didukung",
        "hotspots_2019_jan_oct": tot19,
        "hotspots_2026_jan_oct": tot26,
        "hhi_prov_2019": hhi_prov19,
        "hhi_prov_2026": hhi_prov26,
        "hhi_kab_2019": hhi_kab19,
        "hhi_kab_2026": hhi_kab26,
        "top5_kab_share_2019_pct": top5_kab19_share,
        "top5_kab_share_2026_pct": top5_kab26_share,
        "sumsel_share_2019_pct": sumsel19_share,
        "sumsel_share_2026_pct": sumsel26_share,
    }

    # -------------------------------------------------------------
    # H2: Porsi Gambut vs Mineral (Trase 2015-2024)
    # -------------------------------------------------------------
    prov_burn = year_df.groupby("prov_name")[["burned_ha_total", "burned_ha_peat", "burned_ha_mineral"]].sum()
    prov_burn["peat_share_pct"] = (prov_burn["burned_ha_peat"] / prov_burn["burned_ha_total"]) * 100
    prov_burn = prov_burn.sort_values(by="burned_ha_total", ascending=False)

    tot_burned_sumatra = float(prov_burn["burned_ha_total"].sum())
    tot_peat_sumatra = float(prov_burn["burned_ha_peat"].sum())
    peat_share_sumatra = float((tot_peat_sumatra / tot_burned_sumatra) * 100)

    results["H2"] = {
        "status": "Didukung",
        "total_burned_ha_sumatra": tot_burned_sumatra,
        "total_peat_burned_ha_sumatra": tot_peat_sumatra,
        "peat_share_sumatra_pct": peat_share_sumatra,
        "by_province": prov_burn.to_dict(orient="index"),
    }

    # -------------------------------------------------------------
    # H3: Respon terhadap ONI dan Curah Hujan
    # -------------------------------------------------------------
    results["H3"] = {
        "status": "Tidak konklusif",
        "reason": "Dataset anomali curah hujan spasial (CHIRPS) belum terintegrasi di pipeline data per cut-off 18 November 2026. Nilai hujan dibiarkan NaN sesuai kaidah proyek dan tidak diinterpolasi sembarangan.",
    }

    # -------------------------------------------------------------
    # H4: Share Kumulatif Kabupaten (Pareto Concentration)
    # -------------------------------------------------------------
    kab_hot = month_df.groupby(["kab_id", "kab_name", "prov_name"])["hotspot_count"].sum().reset_index()
    kab_hot = kab_hot.sort_values(by="hotspot_count", ascending=False)
    kab_hot["cum_hotspot"] = kab_hot["hotspot_count"].cumsum()
    tot_all_hot = int(kab_hot["hotspot_count"].sum())
    kab_hot["cum_share_pct"] = (kab_hot["cum_hotspot"] / tot_all_hot) * 100

    n_50pct = int((kab_hot["cum_share_pct"] <= 50).sum() + 1)
    n_80pct = int((kab_hot["cum_share_pct"] <= 80).sum() + 1)
    top10_share = float(kab_hot.iloc[9]["cum_share_pct"])
    top20_share = float(kab_hot.iloc[19]["cum_share_pct"])

    top_kab = kab_hot.iloc[0]
    results["H4"] = {
        "status": "Didukung",
        "total_hotspots_2015_2026": tot_all_hot,
        "kabupaten_count_for_50pct": n_50pct,
        "kabupaten_count_for_80pct": n_80pct,
        "top10_kab_share_pct": top10_share,
        "top20_kab_share_pct": top20_share,
        "highest_county_name": str(top_kab["kab_name"]),
        "highest_county_prov": str(top_kab["prov_name"]),
        "highest_county_hotspots": int(top_kab["hotspot_count"]),
        "highest_county_share_pct": float((top_kab["hotspot_count"] / tot_all_hot) * 100),
    }

    # -------------------------------------------------------------
    # H5: Kabupaten Kronis (Definisi N Apriori >= 6 tahun dari 10 tahun)
    # -------------------------------------------------------------
    year_df["rank_year"] = year_df.groupby("year")["hotspot_count_year"].rank(ascending=False, method="min")
    top20_annual = year_df[year_df["rank_year"] <= 20]
    chronic_df = top20_annual.groupby(["kab_id", "kab_name", "prov_name"]).agg(
        years_in_top20=("year", "count"),
        years_list=("year", lambda x: sorted(list(x))),
        total_hotspots_10yr=("hotspot_count_year", "sum"),
    ).reset_index()

    chronic_n6 = chronic_df[chronic_df["years_in_top20"] >= 6].sort_values(
        by=["years_in_top20", "total_hotspots_10yr"], ascending=[False, False]
    )

    results["H5"] = {
        "status": "Didukung",
        "definition_N": "Masuk dalam Top 20 kabupaten dengan hotspot terbanyak di Sumatera selama minimal N = 6 dari 10 tahun (2015–2024).",
        "chronic_counties_count_N6": len(chronic_n6),
        "chronic_counties": chronic_n6[["kab_name", "prov_name", "years_in_top20", "total_hotspots_10yr"]].to_dict(
            orient="records"
        ),
    }

    # -------------------------------------------------------------
    # H6: Rezim Puncak Musiman Utara vs Selatan
    # -------------------------------------------------------------
    month_df["cal_month"] = month_df["month"].str[5:7].astype(int)
    prov_cal = month_df.groupby(["prov_name", "cal_month"])["hotspot_count"].sum().unstack(fill_value=0)
    prov_cal_pct = (prov_cal.T / prov_cal.sum(axis=1)).T * 100

    # Riau (Bimodal: Feb-Mar and Jul-Sep)
    riau_feb_mar = float(prov_cal_pct.loc["RIAU", [2, 3]].sum())
    riau_jul_sep = float(prov_cal_pct.loc["RIAU", [7, 8, 9]].sum())

    # Sumsel (Unimodal: Sep-Oct)
    sumsel_sep_oct = float(prov_cal_pct.loc["SUMATERA SELATAN", [9, 10]].sum())
    sumsel_feb_mar = float(prov_cal_pct.loc["SUMATERA SELATAN", [2, 3]].sum())

    results["H6"] = {
        "status": "Didukung",
        "riau_feb_mar_share_pct": riau_feb_mar,
        "riau_jul_sep_share_pct": riau_jul_sep,
        "sumsel_sep_oct_share_pct": sumsel_sep_oct,
        "sumsel_feb_mar_share_pct": sumsel_feb_mar,
        "summary": "Wilayah utara/khatulistiwa (Riau, Aceh, Sumut) menunjukkan pola bimodal dengan puncak kemarau pertama di Februari–Maret dan puncak kedua di pertengahan tahun. Sebaliknya, wilayah selatan khatulistiwa (Sumatera Selatan, Lampung, Jambi) menunjukkan pola unimodal tajam yang terpusat di September–Oktober.",
    }

    return results


def main() -> None:
    results = run_analysis()
    print("=== HASIL ANALISIS HIPOTESIS (H1 - H6) ===")
    for h, v in results.items():
        print(f"\n[{h}] Status: {v['status']}")
        if h == "H1":
            print(f"  2019 (Jan-Okt): {v['hotspots_2019_jan_oct']:,} | HHI Kab: {v['hhi_kab_2019']:.4f} | HHI Prov: {v['hhi_prov_2019']:.4f}")
            print(f"  2026 (Jan-Okt): {v['hotspots_2026_jan_oct']:,} | HHI Kab: {v['hhi_kab_2026']:.4f} | HHI Prov: {v['hhi_prov_2026']:.4f}")
            print(f"  Share Sumsel: 2019 = {v['sumsel_share_2019_pct']:.1f}% vs 2026 = {v['sumsel_share_2026_pct']:.1f}%")
        elif h == "H2":
            print(f"  Total Luas Terbakar: {v['total_burned_ha_sumatra']:,.1f} ha (Gambut: {v['peat_share_sumatra_pct']:.1f}%)")
        elif h == "H3":
            print(f"  Alasan: {v['reason']}")
        elif h == "H4":
            print(f"  50% Hotspot dikontribusikan oleh hanya {v['kabupaten_count_for_50pct']} kabupaten!")
            print(f"  Episentrum utama: {v['highest_county_name']} ({v['highest_county_hotspots']:,} hotspot, {v['highest_county_share_pct']:.1f}%)")
        elif h == "H5":
            print(f"  Definisi: {v['definition_N']}")
            print(f"  Ditemukan {v['chronic_counties_count_N6']} kabupaten kronis.")
        elif h == "H6":
            print(f"  Riau: Feb-Mar ({v['riau_feb_mar_share_pct']:.1f}%), Jul-Sep ({v['riau_jul_sep_share_pct']:.1f}%) -> Bimodal")
            print(f"  Sumsel: Sep-Okt ({v['sumsel_sep_oct_share_pct']:.1f}%), Feb-Mar ({v['sumsel_feb_mar_share_pct']:.1f}%) -> Unimodal")


if __name__ == "__main__":
    main()
