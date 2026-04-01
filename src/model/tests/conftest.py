import pytest
from datetime import datetime
from entitymention import EntityMention

@pytest.fixture
def valid_hash():
    """A valid 64-character SHA256 hex string."""
    return "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

@pytest.fixture
def valid_embedding():
    """Provides a valid 768-dimension embedding."""
    return [0.1] * 768

@pytest.fixture
def base_params(valid_hash, valid_embedding):
    """Standard dictionary of parameters for EntityMention."""
    return {
        "origin_id": "source-01",
        "request_id": "req-123",
        "entity_type": "Organization",
        "original_asset": "http://example.org/asset/1",
        "properties": {"name": "Test Entity"},
        "embedding": valid_embedding,
        "cluster_id": valid_hash,
        "similarity_score": 0.85,
        "confidence_score": 0.9,
        "is_medoid": True
    }

@pytest.fixture
def minimal_params():
    """Minimal dictionary for EntityMention — only required fields, no ML fields."""
    return {
        "origin_id": "source-01",
        "request_id": "req-123",
        "entity_type": "Organization",
        "original_asset": "http://example.org/asset/1",
        "properties": {"name": "Test Entity"},
    }

@pytest.fixture
def entity_instance(base_params):
    """A pre-instantiated frozen EntityMention object."""
    return EntityMention(**base_params)