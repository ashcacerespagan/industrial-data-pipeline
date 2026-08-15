# X-Ray & Panel Inspection Data Pipeline ![Run ETL Pipeline Tests](https://github.com/ashcacerespagan/industrial-data-pipeline/actions/workflows/test.yml/badge.svg)

An end-to-end Python and SQLite data engineering pipeline designed to ingest, process, store, and analyze hardware test telemetry and defect logs for X-ray imaging panels.

## 📌 Architecture Overview
- **Data Generation (`src/generate_data.py`)**: Simulates batch telemetry logs including panel serial numbers, model types, operating voltage/current, defect counts, and pass/fail statuses.
- **ETL Ingestion (`src/etl_pipeline.py`)**: Parses incoming raw inspection CSVs, validates test parameters, appends records into an SQLite database, and exports a Git-diffable JSON run summary (`data/latest_inspection_run.json`).
- **Query & Analytics (`src/query_module.py`)**: CLI tool executing analytical SQL queries to evaluate first-pass yield rates across panel models and flag critical hardware defects for technical analysis.
- **Automated CI (`.github/workflows/test.yml`)**: Continuous integration workflow running automated `pytest` suites on every code push.

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.8+
- SQLite3

### Setup & Execution
1. Clone the repository:
   ```bash
   git clone [https://github.com/ashcacerespagan/industrial-data-pipeline.git](https://github.com/ashcacerespagan/industrial-data-pipeline.git)
   cd industrial-data-pipeline