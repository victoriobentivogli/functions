import pytest
import hashlib
import time
from pydantic import ValidationError
from entitymention import EntityMention

def test_entity_id_auto_generation(base_params):
    """Verify SHA256(origin_id:request_id:entity_type) is computed correctly."""
    mention = EntityMention(**base_params)
    
    raw = f"{base_params['origin_id']}:{base_params['request_id']}:{base_params['entity_type']}"
    expected_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    
    assert mention.entity_id == expected_hash

def test_sha256_format_validation(base_params):
    """Ensure cluster_id must be a valid 64-char hex string."""
    base_params["cluster_id"] = "invalid-hash-123"
    with pytest.raises(ValueError, match="Must be a 64-character SHA256 hex string"):
        EntityMention(**base_params)

def test_embedding_dimension_validation(base_params):
    """Ensure embedding must be empty or exactly 768 dimensions."""
    base_params["embedding"] = [0.1, 0.2]  # Wrong size (neither 0 nor 768)
    with pytest.raises(ValueError, match="Embedding must be empty or have exactly 768 elements"):
        EntityMention(**base_params)

def test_immutability(entity_instance):
    """Verify the model is frozen."""
    with pytest.raises(ValidationError):
        entity_instance.cluster_id = "a" * 64

def test_update_record_logic(entity_instance):
    """Verify timestamps and medoid reset during cluster transitions."""
    old_updated_at = entity_instance.updated_at
    new_cluster = "f" * 64
    
    # Small sleep to ensure clock ticks
    time.sleep(0.01)
    
    # Action: Move to a new cluster
    updated = entity_instance.update_record(cluster_id=new_cluster)
    
    assert updated.cluster_id == new_cluster
    assert updated.updated_at > old_updated_at
    assert updated.is_medoid is False  # Should be reset automatically
    assert updated.created_at == entity_instance.created_at # Should remain constant

def test_update_record_manual_medoid(entity_instance):
    """Verify we can override the auto-reset of is_medoid if needed."""
    new_cluster = "b" * 64
    updated = entity_instance.update_record(cluster_id=new_cluster, is_medoid=True)
    
    assert updated.cluster_id == new_cluster
    assert updated.is_medoid is True # Manual override works


def test_minimal_construction(minimal_params):
    """Verify EntityMention can be created with only required fields (no ML fields)."""
    mention = EntityMention(**minimal_params)
    assert mention.origin_id == "source-01"
    assert mention.properties == {"name": "Test Entity"}
    assert mention.embedding == []
    assert mention.cluster_id == ""
    assert mention.similarity_score == 0.0
    assert mention.confidence_score == 0.0
    assert mention.is_medoid is False


def test_empty_embedding_allowed(minimal_params):
    """Verify that an empty embedding list passes validation."""
    mention = EntityMention(**minimal_params)
    assert mention.embedding == []