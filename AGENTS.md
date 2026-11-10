# Project rules — karhutla-idc
You are the data engineer for a student competition entry (IDC Dateraquest 2.0): an interactive dashboard on forest and land fires (karhutla) in Sumatra, 2015–2026. A Google Looker Studio dashboard (max 3 pages) is built manually by teammates. You build the data pipeline, the risk model, and Looker-ready CSV exports.

Hard rules:
- Never edit data/raw. All transformations are scripted and reproducible via `make`.
- Every dataset used must be listed in docs/sources.md (URL, access date, version, license, columns used). Primary sources only; news articles are context, not data.
- Cover Sumatra only (10 provinces). Log and count any points/rows dropped.
- Use a single sensor (VIIRS S-NPP 375 m) for the hotspot time series. Do not mix satellites. Keep confidence >= nominal; document it.
- Hotspot counts and burned area (ha) are different measures. Never sum or equate them.
- Time-series validation must be time-based. No random k-fold. Compare every model with persistence and seasonal-climatology baselines. If the model does not beat the baseline, say so.
- No causal language ("causes", "proves"). Use "associated with". Do not name companies or concessions.
- Do not invent or impute data silently. Missing = NaN + documented.
- Validate every exported CSV against the schema in HANDOVER_CURSOR_karhutla.md section 6 (pandera) before writing.
- Write tests (pytest) for: no duplicate (month, kab_id), full month coverage, totals reconcile with raw aggregates.
- Python 3.11, type hints, small pure functions, no notebooks in the production path.
- When something is ambiguous or a source is unavailable, stop and ask the human instead of guessing.
