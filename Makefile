PYTHON ?= python

.PHONY: ingest ingest-oni ingest-boundaries ingest-trase crosswalk-review build model export check

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

model:
	@echo "model belum dibuat. Tahap S5 belum dimulai." && exit 2

export:
	@echo "export belum dibuat. Tahap S6 belum dimulai." && exit 2

check:
	$(PYTHON) -m pytest
