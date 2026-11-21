PYTHON ?= python

.PHONY: ingest ingest-oni ingest-boundaries ingest-trase crosswalk-review build dim model export check

ingest: ingest-oni ingest-boundaries ingest-trase

ingest-oni:
	$(PYTHON) -m src.ingest.oni

ingest-boundaries:
	$(PYTHON) -m src.ingest.boundaries

ingest-trase:
	$(PYTHON) -m src.ingest.trase

crosswalk-review:
	$(PYTHON) -m src.transform.crosswalk

build:
	$(PYTHON) -m src.transform.spatial_join
	$(PYTHON) -m src.transform.build_panel
	$(PYTHON) -m src.ingest.build_dim_kabupaten

dim:
	$(PYTHON) -m src.ingest.build_dim_kabupaten

model: build
	$(PYTHON) -m src.model.train

export: model
	$(PYTHON) -m src.export.build_exports
	$(PYTHON) -m src.model.forecast

check:
	$(PYTHON) -m pytest
