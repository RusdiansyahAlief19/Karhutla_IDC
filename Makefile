PYTHON ?= python

.PHONY: ingest ingest-oni ingest-boundaries build model export check

ingest: ingest-oni ingest-boundaries

ingest-oni:
	$(PYTHON) -m src.ingest.oni

ingest-boundaries:
	$(PYTHON) -m src.ingest.boundaries

build:
	@echo "build belum dibuat. Tahap S3 belum dimulai." && exit 2

model:
	@echo "model belum dibuat. Tahap S5 belum dimulai." && exit 2

export:
	@echo "export belum dibuat. Tahap S6 belum dimulai." && exit 2

check:
	$(PYTHON) -m pytest
