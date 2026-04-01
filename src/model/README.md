# ERE Model

Shared Pydantic models for the **Entity Resolution Engine (ERE)**.

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
# From the src/model directory
uv sync
```

---

## EntityMention Data Model
A robust, Pydantic-powered data model for representing entity mentions within the Entity Resolution Engine (ERE). 

This model ensures data integrity through immutability, automated identity hashing, and strict format validation.

### Features

- Immutable: Uses Pydantic frozen=True to prevent accidental state changes during processing.
- Deterministic ID: entity_id is automatically calculated as SHA256(origin_id:request_id:entity_type).
- Validation: Enforces 768-dimension embeddings and SHA256 hex formats for cluster identifiers.
- Smart Timestamps: Automatically manages created_at and updated_at during record transitions.

Modern Tooling: Fully integrated with uv, pytest, and ruff.

### Usage

```python
from entitymention import EntityMention

# Create a mention (entity_id and timestamps are handled automatically)
mention = EntityMention(
    origin_id="notice-001",
    request_id="req-550e8400",
    entity_type="http://www.w3.org/ns/org/Organization",
    original_asset="http://data.europa.eu/a4g/resource/notice-001/Organization/ORG-0001",
    properties={
        "hasLegalName": "FORSYNING HELSINGØR A/S",
        "hasPrimaryContactPoint.email": "cnor@servia.dk",
    },
    embedding=[0.1] * 768,
    cluster_id="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    similarity_score=0.98,
    confidence_score=0.95,
    is_medoid=True
)

# Automated Field Access
print(mention.entity_id)   # Generated SHA256 hash
print(mention.created_at)  # Timestamp at instantiation

# Update the record (returns a new frozen instance with refreshed updated_at)
new_cluster = "5f19001155822bf66236315264878a873cc78ed17ca410" # Must be 64-char hex
updated_mention = mention.update_record(cluster_id=new_cluster)

# Note: is_medoid is auto-reset to False when cluster_id changes
print(updated_mention.is_medoid) # False
```

### API Reference

#### `EntityMention`

| Field | Type | Description |
|-------|------|-------------|
| `origin_id` | `str` | `Unique identifier for the data origin.` |
| `request_id` | `str` | `Client-assigned request identifier for tracking.` |
| `entity_type` | `str` | `The type (i.e.: rdf:type URI) of the entity.` |
| `entity_id` | `str` | `Auto-generated: SHA256(origin_id:request_id:entity_type).` |
| `original_asset` | `str` | `The unmodified textual representation of the entity.` |
| `properties` | `dict` | `Flat property map (supports dot-notation and list[str]).` |
| `embedding` | `list[float]` | `Vector (of N dimensions) for similarity.` |
| `cluster_id` | `str` | `SHA256 hex: Identifier for the assigned cluster.` |
| `similarity_score` | `float` | `Score relative to a reference or cluster medoid.` |
| `confidence_score` | `float` | `Reliability score of the assignement of the entiry to its cluster.` |
| `is_medoid` | `bool` | `True if this mention represents its cluster.` |
| `created_at` | `datetime` | `Auto-generated: Timestamp at creation.` |
| `updated_at` | `datetime` | `Auto-generated: Refreshed via .update_record().` |

---

## Developer Guide 

### Development Workflow

| Command | Description |
|---------|-------------|
| ´make sync´ | ´Syncs .venv with pyproject.toml.´ | 
| ´make test´ | ´Runs pytest suite with coverage.´ | 
| ´make lint´ | ´Checks code style with ruff.´ | 
| ´make format´ | ´Formats code with ruff.´ | 
| ´make clean´ | ´Clears all caches and virtual environments.´ | 

--- 
## CI/CD

The main project uses GitHub Actions (´.github/workflows/python-tests.yml´). On every push to the ´develop´ branch, 
the suite is executed using ´uv´ to ensure 100% logic and validation consistency.