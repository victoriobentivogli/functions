# EntityMention Cleaner

Cleans and normalizes `EntityMention` properties for the **Entity Resolution Engine (ERE)**.

This is the second stage of the ERE pipeline. It receives an `EntityMention` (populated by the rdf-entitymention-extractor) and returns a new instance with cleaned/normalized properties.

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
# From the src/entitymention-cleaner directory
uv sync
```

To include development dependencies (pytest):

```bash
uv sync --extra dev
```

---

## Usage

```python
from entitymention_cleaner import entitymention_cleaner

# mention is an EntityMention instance from the extractor
cleaned = entitymention_cleaner(mention)
```

---

## API

### `entitymention_cleaner(mention) -> EntityMention`

| Parameter | Type | Description |
|-----------|------|-------------|
| `mention` | `EntityMention` | Entity mention with properties to clean |

**Returns** a new `EntityMention` instance with cleaned `properties` and a refreshed `updated_at` timestamp.

**Pipeline fields modified**: `properties`, `updated_at`

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
