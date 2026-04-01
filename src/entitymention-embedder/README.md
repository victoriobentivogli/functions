# EntityMention Embedder

Calculates embeddings for `EntityMention` properties in the **Entity Resolution Engine (ERE)**.

This is the third stage of the ERE pipeline. It receives a cleaned `EntityMention` and returns a new instance with the `embedding` field populated (768-dimension vector).

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
# From the src/entitymention-embedder directory
uv sync
```

To include development dependencies (pytest):

```bash
uv sync --extra dev
```

---

## Usage

```python
from entitymention_embedder import entitymention_embedder

# mention is a cleaned EntityMention instance
embedded = entitymention_embedder(mention)

# With custom property weights
embedded = entitymention_embedder(
    mention,
    property_weights={"hasLegalName": 0.6, "registeredAddress.fullAddress": 0.4},
)
```

---

## API

### `entitymention_embedder(mention, property_weights) -> EntityMention`

| Parameter | Type | Description |
|-----------|------|-------------|
| `mention` | `EntityMention` | Entity mention with cleaned properties to embed |
| `property_weights` | `dict[str, float]` or `None` | Optional weights for each property's contribution to the combined embedding. When `None`, all properties contribute equally. |

**Returns** a new `EntityMention` instance with the `embedding` field set (768-dimension vector) and a refreshed `updated_at` timestamp.

**Pipeline fields filled**: `embedding`

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
