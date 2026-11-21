# karhutla-idc

Reproducible data pipeline, analysis, and risk projections for an interactive
dashboard on forest and land fires in Sumatra, 2015–2026. The Looker Studio
dashboard is built separately by the team.

## Environment

Use Python 3.11 and install the pipeline and development dependencies:

```powershell
python -m pip install -e ".[pipeline,dev]"
```

The current handover workspace has Python 3.10.11 and no Python 3.11 install;
the test suite has passed on 3.10.11, but model and export runs should use 3.11.

## Pipeline

`make build` rebuilds the spatial join, monthly and annual panels, and county
geometry dimension from the local raw files. `make model` also builds model
artifacts after rebuilding the inputs. `make export` builds the model, validates
and writes the schema-defined exports, then validates and writes the forecast.

Equivalent module commands from the repository root:

```powershell
python -m src.transform.spatial_join
python -m src.transform.build_panel
python -m src.ingest.build_dim_kabupaten
python -m pytest
python -m src.model.train
python -m src.export.build_exports
python -m src.model.forecast
```

Ingest commands (`make ingest`) download only the URLs listed in
`docs/sources.md`. They do not overwrite `data/raw`; changed content stops the
ingest and the checksum manifest is maintained separately.

## Data and outputs

- Hotspot counts use one sensor: VIIRS S-NPP 375 m. The data end on 31 October
  2026. Archive and NRT labels are kept separate in `data_quality`.
- Trase burned area, burned peat, and derived mineral area are annual measures
  for 2015–2024. They are not monthly and are not hotspot counts.
- CHIRPS, county peatland-cover share, and population are not ingested. Their
  output fields stay `NaN`; rainfall-related findings remain inconclusive.
- `data/processed` contains the Pandera-validated `dim_kabupaten.csv`,
  `fact_kab_month.csv`, `fact_kab_year.csv`, `prov_summary_year.csv`, and
  `ml_risk_forecast.csv` exports.
- `model_metrics.csv` and `feature_importance.csv` have no approved column
  contract yet, so the training command does not write those files.
- A pre-existing local `model_metrics.csv` may be from an older run; the current
  training command does not refresh it, so do not treat it as current results.

See [docs/methodology.md](docs/methodology.md), [docs/data_dictionary.md](docs/data_dictionary.md),
and [docs/sources.md](docs/sources.md) for definitions and source coverage.
