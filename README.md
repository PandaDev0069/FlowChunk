# FlowChunk

FlowChunk is a small FastAPI service backed by Postgres and Alembic migrations.

## Local setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations:

```bash
alembic revision --autogenerate -m "Initial migration"
```

```bash
alembic upgrade head
```

Run tests:

```bash
python -m pytest
```

Lint and format:

```bash
ruff check .
ruff format .
```

Access DB:

```bash
docker exec -it flowchunk-db psql -U flowchunk -d flowchunk
```

Generate pytest coverage report:

```bash
python -m pytest --cov=app --cov-report=html

```

Check coverage report:

```bash
python -m coverage html
```
