# DB Manager

Database operations for `EntityMention` persistence in the **Entity Resolution Engine (ERE)**.

Uses **PostgreSQL** with **pgvector** for vector storage and similarity search. Provides CRUD functions for storing, retrieving, listing, and deleting `EntityMention` instances. Includes a **docker-compose** setup with **pgAdmin** for local development.

---

## Requirements

| Tool | Version |
|------|---------|
| Python | >= 3.12 |
| [uv](https://docs.astral.sh/uv/) | any recent |
| [Docker](https://docs.docker.com/get-docker/) | any recent |
| `make` | any recent |

---

## Quick Start

```bash
# 1. Start the database
make db-up

# 2. Install Python dependencies
make sync

# 3. Run tests
make test

# 4. Stop when done
make db-down
```

---

## Infrastructure

### Starting the database

```bash
make db-up
```

This starts two containers:

| Service | URL | Credentials |
|---------|-----|-------------|
| PostgreSQL | `localhost:5433` | user: `ere` / password: `ere` / db: `ere` |
| pgAdmin | `http://localhost:5051` | email: `admin@ere.local` / password: `admin` |

The database is automatically initialised with the `pgvector` extension and the `entity_mentions` table on first start (via `sql/init.sql`).

### pgAdmin

Open `http://localhost:5051` in your browser. To connect to the database from pgAdmin, add a new server with:

| Field | Value |
|-------|-------|
| Host | `postgres` (Docker service name) |
| Port | `5432` |
| Username | `ere` |
| Password | `ere` |
| Database | `ere` |

### Other infrastructure commands

```bash
make db-down    # Stop containers
make db-reset   # Destroy data volume and recreate (clean slate)
make db-logs    # Follow container logs
make db-psql    # Open a psql shell inside the container
```

---

## Connection

The module reads the `DATABASE_URL` environment variable. Default:

```
DATABASE_URL=postgresql://ere:ere@localhost:5433/ere
```

See `.env.example` for reference.

---

## Installation

```bash
# From the src/db-manager directory
uv sync
```

To include development dependencies (pytest):

```bash
uv sync --extra dev
```

---

## Usage

```python
from db_manager import save_entitymention, get_entitymention, list_entitymentions, delete_entitymention

# Save an EntityMention (upsert)
saved = save_entitymention(mention)

# Retrieve by entity_id
found = get_entitymention("e3b0c44298fc1c149afbf4c8996fb924...")

# List all, or filter by cluster
all_mentions = list_entitymentions()
cluster_mentions = list_entitymentions(cluster_id="a1b2c3...")

# Delete
deleted = delete_entitymention("e3b0c44298fc1c149afbf4c8996fb924...")
```

---

## API

### `save_entitymention(mention) -> EntityMention`

| Parameter | Type | Description |
|-----------|------|-------------|
| `mention` | `EntityMention` | The entity mention to persist (upsert) |

**Returns** the saved `EntityMention` instance as read back from the database.

### `get_entitymention(entity_id) -> EntityMention | None`

| Parameter | Type | Description |
|-----------|------|-------------|
| `entity_id` | `str` | SHA256 identifier of the entity mention |

**Returns** the matching `EntityMention`, or `None` if not found.

### `list_entitymentions(cluster_id) -> list[EntityMention]`

| Parameter | Type | Description |
|-----------|------|-------------|
| `cluster_id` | `str` or `None` | Optional cluster filter. When `None`, returns all. |

**Returns** a list of matching `EntityMention` instances.

### `delete_entitymention(entity_id) -> bool`

| Parameter | Type | Description |
|-----------|------|-------------|
| `entity_id` | `str` | SHA256 identifier of the entity mention to delete |

**Returns** `True` if deleted, `False` if not found.

---

## Database Schema

```sql
CREATE TABLE entity_mentions (
    entity_id        CHAR(64) PRIMARY KEY,
    origin_id        TEXT NOT NULL,
    request_id       TEXT NOT NULL,
    entity_type      TEXT NOT NULL,
    original_asset   TEXT NOT NULL,
    properties       JSONB NOT NULL DEFAULT '{}',
    embedding        vector(768),
    cluster_id       CHAR(64),
    similarity_score DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    confidence_score DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    is_medoid        BOOLEAN NOT NULL DEFAULT FALSE,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

## Developer Guide

### Development Workflow

| Command | Description |
|---------|-------------|
| `make db-up` | Start PostgreSQL + pgAdmin containers. |
| `make db-down` | Stop containers. |
| `make db-reset` | Destroy data and recreate containers. |
| `make db-logs` | Follow container logs. |
| `make db-psql` | Open psql shell in the container. |
| `make sync` | Syncs .venv with pyproject.toml. |
| `make test` | Runs pytest suite (requires `db-up`). |
| `make lint` | Checks code style with ruff. |
| `make format` | Formats code with ruff. |
| `make clean` | Clears all caches and virtual environments. |
