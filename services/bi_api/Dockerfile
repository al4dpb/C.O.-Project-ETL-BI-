FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc curl ca-certificates && rm -rf /var/lib/apt/lists/*

COPY services/bi_api/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY services/bi_api /app/services/bi_api
COPY ["C.O. Project (ETL+BI)/sql_queries", "/app/sql_queries"]

ENV WAREHOUSE_PATH=/app/data/warehouse.duckdb

EXPOSE 8080

CMD ["uvicorn", "services.bi_api.main:app", "--host", "0.0.0.0", "--port", "8080"]
