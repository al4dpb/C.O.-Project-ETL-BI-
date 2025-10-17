-- MotherDuck Warehouse Setup for Container Offices BI
-- Run this in MotherDuck console or via DuckDB CLI with MotherDuck connection

-- ============================================================
-- DATABASE SETUP
-- ============================================================

-- Create database (if not exists)
CREATE DATABASE IF NOT EXISTS co_warehouse;

USE co_warehouse;

-- ============================================================
-- SCHEMA SETUP
-- ============================================================

-- Create schemas for data layers
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;
CREATE SCHEMA IF NOT EXISTS gold;

-- ============================================================
-- BRONZE EXTERNAL TABLES (S3)
-- ============================================================

-- Dashboard monthly data from S3
CREATE OR REPLACE VIEW bronze.raw_dashboard_monthly AS
SELECT * FROM read_parquet('s3://co-data-<ENV>/bronze/raw_dashboard_monthly/**/*.parquet',
    hive_partitioning=1);

-- Expenses monthly data from S3
CREATE OR REPLACE VIEW bronze.raw_expenses_monthly AS
SELECT * FROM read_parquet('s3://co-data-<ENV>/bronze/raw_expenses_monthly/**/*.parquet',
    hive_partitioning=1);

-- Lease rate snapshot from S3
CREATE OR REPLACE VIEW bronze.raw_lease_rate_snapshot AS
SELECT * FROM read_parquet('s3://co-data-<ENV>/bronze/raw_lease_rate_snapshot/**/*.parquet',
    hive_partitioning=1);

-- ============================================================
-- METADATA TABLES
-- ============================================================

-- Pipeline run log
CREATE TABLE IF NOT EXISTS bronze.pipeline_runs (
    run_id VARCHAR PRIMARY KEY,
    run_timestamp TIMESTAMP,
    pipeline_name VARCHAR,
    status VARCHAR,  -- success, failed, running
    records_processed INTEGER,
    duration_seconds DOUBLE,
    error_message VARCHAR,
    metadata JSON
);

-- Data quality checks log
CREATE TABLE IF NOT EXISTS bronze.quality_checks (
    check_id VARCHAR PRIMARY KEY,
    run_id VARCHAR,
    check_timestamp TIMESTAMP,
    table_name VARCHAR,
    check_type VARCHAR,
    passed BOOLEAN,
    failure_count INTEGER,
    details JSON,
    FOREIGN KEY (run_id) REFERENCES bronze.pipeline_runs(run_id)
);

-- ============================================================
-- GRANTS (if using MotherDuck sharing)
-- ============================================================

-- Grant read access to staging/marts/gold for BI users
-- GRANT SELECT ON staging.* TO <bi_user_email>;
-- GRANT SELECT ON marts.* TO <bi_user_email>;
-- GRANT SELECT ON gold.* TO <bi_user_email>;

-- ============================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================

-- Add indexes after dbt models are created
-- CREATE INDEX IF NOT EXISTS idx_prop_kpi_month ON gold.prop_kpi_monthly(month);
-- CREATE INDEX IF NOT EXISTS idx_building_kpi_month ON gold.building_kpi_monthly(month, building);

COMMENT ON DATABASE co_warehouse IS 'Container Offices Data Warehouse - Production Analytics';
