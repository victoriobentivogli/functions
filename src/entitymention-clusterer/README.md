# EntityMention Clusterer

Calculates clusters from `EntityMention` embeddings for the **Entity Resolution Engine (ERE)**.

This is the final analytical stage of the ERE pipeline. It receives a list of `EntityMention` instances (with embeddings) and returns updated instances with clustering fields populated.

---

## Requirements

| Tool | Version |
|------|---------|
| Python | >= 3.12 |
| [uv](https://docs.astral.sh/uv/) | any recent |
| `make` | any recent |

---

## Installation

```bash
# From the src/entitymention-clusterer directory
uv sync
```

To include development dependencies (pytest):

```bash
uv sync --extra dev
```

---

## Usage

```python
from entitymention_clusterer import entitymention_clusterer

# mentions is a list of EntityMention instances with embeddings
clustered = entitymention_clusterer(mentions)

for m in clustered:
    print(m.cluster_id, m.similarity_score, m.is_medoid)
```

---

## API

### `entitymention_clusterer(mentions) -> list[EntityMention]`

| Parameter | Type | Description |
|-----------|------|-------------|
| `mentions` | `list[EntityMention]` | Entity mentions with embeddings to cluster |

**Returns** a list of new `EntityMention` instances with clustering fields set and refreshed `updated_at` timestamps.

**Pipeline fields filled**: `cluster_id`, `similarity_score`, `confidence_score`, `is_medoid`

---

## Developer Guide

### Development Workflow

| Command | Description |
|---------|-------------|
| `make sync` | Syncs .venv with pyproject.toml. |
| `make test` | Runs pytest suite. |
| `make lint` | Checks code style with ruff. |
| `make format` | Formats code with ruff. |
| `make clean` | Clears all caches and virtual environments. |
