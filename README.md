# FlowChunk

FlowChunk is a small FastAPI service backed by Postgres and Alembic migrations.

## Local setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations:

```bash
alembic upgrade head
```

Run tests:

```bash
pytest
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
