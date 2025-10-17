"""
Container Offices BI API
FastAPI service for querying MotherDuck/DuckDB warehouse
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import duckdb
import pandas as pd

app = FastAPI(
    title="Container Offices BI API",
    description="REST API for Container Offices analytics data",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SQL queries directory
SQL_QUERIES_DIR = Path("/app/sql_queries")


def _conn():
    """
    Get DuckDB connection - MotherDuck if token available, else local file
    """
    token = os.getenv("MOTHERDUCK_TOKEN")
    if token:
        conn_str = f"md:?motherduck_token={token}"
        return duckdb.connect(conn_str, read_only=True)

    warehouse_path = os.getenv("WAREHOUSE_PATH", "data/warehouse.duckdb")
    return duckdb.connect(warehouse_path, read_only=True)


class QueryRequest(BaseModel):
    """Query request with optional parameters"""
    params: Optional[Dict[str, Any]] = None


class QueryResponse(BaseModel):
    """Query response with data and metadata"""
    data: List[Dict[str, Any]]
    row_count: int
    columns: List[str]
    query_name: str


@app.get("/v1/health")
def health():
    """Health check endpoint"""
    try:
        conn = _conn()
        result = conn.execute("SELECT 1 as health").fetchone()
        conn.close()

        return {
            "status": "healthy",
            "database": "motherduck" if os.getenv("MOTHERDUCK_TOKEN") else "local",
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.post("/v1/query/{query_name}", response_model=QueryResponse)
def execute_query(query_name: str, request: QueryRequest = QueryRequest()):
    """
    Execute a named SQL query from sql_queries directory

    Args:
        query_name: Name of SQL file (without .sql extension)
        request: Optional query parameters for parameterized queries
    """
    sql_file = SQL_QUERIES_DIR / f"{query_name}.sql"

    if not sql_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Query '{query_name}' not found. Available queries: {[f.stem for f in SQL_QUERIES_DIR.glob('*.sql')]}"
        )

    # Read SQL query
    query = sql_file.read_text()

    # Replace parameters if provided
    if request.params:
        for key, value in request.params.items():
            placeholder = f"${{{key}}}"
            if isinstance(value, str):
                query = query.replace(placeholder, f"'{value}'")
            else:
                query = query.replace(placeholder, str(value))

    try:
        conn = _conn()
        df = conn.execute(query).df()
        conn.close()

        # Convert DataFrame to list of dicts
        data = df.to_dict(orient="records")

        return QueryResponse(
            data=data,
            row_count=len(data),
            columns=df.columns.tolist(),
            query_name=query_name
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query execution failed: {str(e)}"
        )


@app.get("/v1/queries")
def list_queries():
    """List all available SQL queries"""
    queries = [f.stem for f in SQL_QUERIES_DIR.glob("*.sql")]
    return {
        "queries": sorted(queries),
        "count": len(queries)
    }


@app.get("/v1/tables")
def list_tables():
    """List all tables in the warehouse"""
    try:
        conn = _conn()
        tables = conn.execute("""
            SELECT table_schema, table_name, table_type
            FROM information_schema.tables
            WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
            ORDER BY table_schema, table_name
        """).df()
        conn.close()

        return {
            "tables": tables.to_dict(orient="records"),
            "count": len(tables)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list tables: {str(e)}"
        )


@app.post("/v1/sql")
def execute_sql(request: QueryRequest):
    """
    Execute arbitrary SQL query (use with caution - read-only connection)

    Args:
        request: Must include 'query' in params
    """
    if not request.params or 'query' not in request.params:
        raise HTTPException(
            status_code=400,
            detail="'query' parameter required in request body"
        )

    query = request.params['query']

    try:
        conn = _conn()
        df = conn.execute(query).df()
        conn.close()

        return {
            "data": df.to_dict(orient="records"),
            "row_count": len(df),
            "columns": df.columns.tolist()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"SQL execution failed: {str(e)}"
        )


# Import and mount upload router
from services.bi_api.upload import router as upload_router
app.include_router(upload_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
