"""Configuration and constants for Container Offices ETL."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR = DATA_DIR / "gold"
WAREHOUSE_PATH = DATA_DIR / "warehouse.duckdb"

# Excel source
EXCEL_PATH = os.getenv("EXCEL_PATH", str(RAW_DIR / "TCO Excel.xlsx"))

# Business constants
TOTAL_SQFT = int(os.getenv("TOTAL_SQFT", "9917"))

# Sheet name patterns (flexible matching)
DASHBOARD_SHEET_PATTERNS = ["dashboard", "2025", "2026"]
LEASE_RATE_SHEET_PATTERNS = ["lease", "rate"]
EXPENSE_SHEET_PATTERNS = ["expense", "gastos", "budget"]

# Column name mappings (EN/ES variants)
COLUMN_ALIASES = {
    # Dashboard columns
    "mes": "month",
    "month": "month",
    "renta base": "rent_base",
    "rent base": "rent_base",
    "base rent": "rent_base",
    "cobrado": "collected",
    "collected": "collected",
    "no cobrado": "uncollected",
    "uncollected": "uncollected",
    "m2 rentados": "leased_sqft",
    "leased sqft": "leased_sqft",
    "sqft arrendado": "leased_sqft",
    "precio m2/año": "price_per_sf_yr",
    "price per sf/yr": "price_per_sf_yr",
    "$/sf/yr": "price_per_sf_yr",

    # Expense columns
    "concepto": "item",
    "item": "item",
    "proveedor": "vendor",
    "vendor": "vendor",
    "real": "actual",
    "actual": "actual",
    "presupuesto": "budget",
    "budget": "budget",
    "varianza": "variance",
    "variance": "variance",

    # Lease/Rate columns
    "suite": "suite_id",
    "suite_id": "suite_id",
    "edificio": "building",
    "building": "building",
    "inquilino": "tenant",
    "tenant": "tenant",
    "m2": "sqft",
    "sqft": "sqft",
    "renta mensual": "rent_monthly",
    "rent monthly": "rent_monthly",
    "monthly rent": "rent_monthly",
    "renta anual": "rent_annual",
    "rent annual": "rent_annual",
    "annual rent": "rent_annual",
    "renta $/m2/año": "rent_psf_yr",
    "rent psf yr": "rent_psf_yr",
    "$/sf/yr": "rent_psf_yr",
}

# Own-use patterns (for flagging internal/non-revenue suites)
OWN_USE_PATTERNS = [
    "black label",
    "owner use",
    "uso propio",
    "101b",  # Known owner suite
]

# Vacancy patterns
VACANCY_PATTERNS = [
    "vacante",
    "vacant",
    "disponible",
    "available",
]

# Ingestion log
INGESTION_LOG_PATH = DATA_DIR / "ingestion_log.csv"

# Bronze partition paths (append-only)
BRONZE_PARTITIONS = {
    "dashboard": BRONZE_DIR / "raw_dashboard_monthly",
    "expenses": BRONZE_DIR / "raw_expenses_monthly",
    "lease_rate": BRONZE_DIR / "raw_lease_rate_snapshot",
}
