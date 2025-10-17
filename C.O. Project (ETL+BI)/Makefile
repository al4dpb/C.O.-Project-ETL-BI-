.PHONY: init run dbt snapshot test clean format lint dashboard forecast help

# V2: Full pipeline with history, windows, and forecasting

init:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip
	. .venv/bin/activate && pip install -e .
	cp .env.example .env
	@echo "✓ Environment initialized. Activate with: source .venv/bin/activate"

run:
	@echo "Running full ETL+BI pipeline (V2)..."
	python -m etl.ingest_excel
	python -m etl.quality
	cd warehouse/dbt && dbt seed
	cd warehouse/dbt && dbt run
	cd warehouse/dbt && dbt snapshot
	cd warehouse/dbt && dbt test
	python -m predict.forecast
	python -m etl.export_gold
	@echo "✓ Pipeline completed successfully"

ingest:
	python -m etl.ingest_excel

ingest-file:
	@if [ -z "$(FILE)" ]; then \
		echo "Error: FILE parameter required. Usage: make ingest-file FILE=path/to/file.xlsx"; \
		exit 1; \
	fi
	python -m etl.ingest_excel --file "$(FILE)"

quality:
	python -m etl.quality

dbt:
	cd warehouse/dbt && dbt seed
	cd warehouse/dbt && dbt run
	cd warehouse/dbt && dbt test

snapshot:
	cd warehouse/dbt && dbt snapshot

dbt-full:
	cd warehouse/dbt && dbt seed
	cd warehouse/dbt && dbt run
	cd warehouse/dbt && dbt snapshot
	cd warehouse/dbt && dbt test

dbt-refresh:
	cd warehouse/dbt && dbt run --full-refresh
	cd warehouse/dbt && dbt snapshot
	cd warehouse/dbt && dbt test

forecast:
	python -m predict.forecast

forecast-excl-own-use:
	python -m predict.forecast --exclude-own-use

export:
	python -m etl.export_gold

test:
	pytest -v

dashboard:
	@echo "Starting Container Offices BI Dashboard (V2)..."
	@echo "Open http://127.0.0.1:8050 in your browser"
	python run_dashboard.py

format:
	black etl/ tests/ dashboard/ predict/
	ruff check --fix etl/ tests/ dashboard/ predict/

lint:
	ruff check etl/ tests/ dashboard/ predict/
	black --check etl/ tests/ dashboard/ predict/

clean:
	rm -rf data/bronze/raw_dashboard_monthly/
	rm -rf data/bronze/raw_expenses_monthly/
	rm -rf data/bronze/raw_lease_rate_snapshot/
	rm -rf data/bronze/_errors/
	rm -rf data/gold/*.csv
	rm -rf data/gold/*.parquet
	rm -rf data/warehouse.duckdb*
	rm -rf data/models/
	rm -rf warehouse/dbt/target/
	rm -rf warehouse/dbt/logs/
	@echo "✓ Cleaned data and build artifacts"

clean-all: clean
	rm -rf .venv
	rm -rf data/ingestion_log.csv
	@echo "✓ Cleaned everything (including venv)"

help:
	@echo "Container Offices ETL+BI Pipeline V2"
	@echo ""
	@echo "Available commands:"
	@echo "  make init                - Initialize environment (first time setup)"
	@echo "  make run                 - Run full pipeline (ingest → quality → dbt → forecast → export)"
	@echo "  make ingest              - Ingest Excel file (uses default from .env)"
	@echo "  make ingest-file FILE=<path> - Ingest specific Excel file"
	@echo "  make quality             - Run data quality checks"
	@echo "  make dbt                 - Run dbt models only"
	@echo "  make snapshot            - Run dbt snapshots (SCD2)"
	@echo "  make dbt-full            - Run dbt seed + run + snapshot + test"
	@echo "  make dbt-refresh         - Rebuild dbt models from scratch"
	@echo "  make forecast            - Generate KPI forecasts"
	@echo "  make forecast-excl-own-use - Forecast with own-use excluded"
	@echo "  make export              - Export gold tables to CSV"
	@echo "  make dashboard           - Launch interactive BI dashboard"
	@echo "  make test                - Run pytest"
	@echo "  make format              - Format code with black/ruff"
	@echo "  make lint                - Lint code"
	@echo "  make clean               - Remove data artifacts"
	@echo "  make clean-all           - Remove everything including venv"
	@echo "  make help                - Show this help message"
