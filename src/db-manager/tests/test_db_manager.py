"""
Integration tests for db_manager.py

Requires a running PostgreSQL+pgvector instance.
Start one with: make db-up
Tests are skipped automatically when the database is unreachable.
"""

import os

import psycopg
import pytest
from entitymention import EntityMention
from db_manager import (
    save_entitymention,
    get_entitymention,
    list_entitymentions,
    delete_entitymention,
)

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://ere:ere@localhost:5433/ere",
)


def _db_is_reachable() -> bool:
    try:
        with psycopg.connect(DATABASE_URL, connect_timeout=3):
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _db_is_reachable(),
    reason=f"PostgreSQL not reachable at {DATABASE_URL}",
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _clean_table():
    """Truncate the table before each test for isolation."""
    with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
        conn.execute("TRUNCATE entity_mentions")
    yield


@pytest.fixture
def sample_mention():
    """A minimal EntityMention for testing."""
    return EntityMention(
        origin_id="test-origin",
        request_id="test-request",
        entity_type="http://www.w3.org/ns/org/Organization",
        original_asset="http://example.org/Organization/ORG-0001",
        properties={"hasLegalName": "Test Org", "email": "test@example.org"},
    )


@pytest.fixture
def mention_with_embedding():
    """An EntityMention with a 768-dim embedding."""
    return EntityMention(
        origin_id="embed-origin",
        request_id="embed-request",
        entity_type="http://www.w3.org/ns/org/Organization",
        original_asset="http://example.org/Organization/ORG-0002",
        properties={"hasLegalName": "Embedded Org"},
        embedding=[0.1] * 768,
    )


@pytest.fixture
def mention_with_cluster():
    """An EntityMention with clustering fields populated."""
    return EntityMention(
        origin_id="cluster-origin",
        request_id="cluster-request",
        entity_type="http://www.w3.org/ns/org/Organization",
        original_asset="http://example.org/Organization/ORG-0003",
        properties={"hasLegalName": "Clustered Org"},
        embedding=[0.5] * 768,
        cluster_id="a" * 64,
        similarity_score=0.95,
        confidence_score=0.88,
        is_medoid=True,
    )


# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------


class TestSave:
    def test_save_returns_entitymention(self, sample_mention):
        result = save_entitymention(sample_mention)
        assert isinstance(result, EntityMention)

    def test_save_persists_fields(self, sample_mention):
        save_entitymention(sample_mention)
        loaded = get_entitymention(sample_mention.entity_id)
        assert loaded is not None
        assert loaded.origin_id == sample_mention.origin_id
        assert loaded.request_id == sample_mention.request_id
        assert loaded.entity_type == sample_mention.entity_type
        assert loaded.original_asset == sample_mention.original_asset
        assert loaded.entity_id == sample_mention.entity_id

    def test_save_persists_properties(self, sample_mention):
        save_entitymention(sample_mention)
        loaded = get_entitymention(sample_mention.entity_id)
        assert loaded.properties == sample_mention.properties

    def test_upsert_updates_existing(self, sample_mention):
        save_entitymention(sample_mention)
        updated = sample_mention.update_record(
            properties={"hasLegalName": "Updated Org"},
        )
        save_entitymention(updated)
        loaded = get_entitymention(sample_mention.entity_id)
        assert loaded.properties == {"hasLegalName": "Updated Org"}

    def test_upsert_does_not_duplicate(self, sample_mention):
        save_entitymention(sample_mention)
        save_entitymention(sample_mention)
        all_mentions = list_entitymentions()
        assert len(all_mentions) == 1


# ---------------------------------------------------------------------------
# Get
# ---------------------------------------------------------------------------


class TestGet:
    def test_get_existing(self, sample_mention):
        save_entitymention(sample_mention)
        loaded = get_entitymention(sample_mention.entity_id)
        assert loaded is not None
        assert loaded.entity_id == sample_mention.entity_id

    def test_get_nonexistent_returns_none(self):
        result = get_entitymention("f" * 64)
        assert result is None

    def test_get_preserves_timestamps(self, sample_mention):
        save_entitymention(sample_mention)
        loaded = get_entitymention(sample_mention.entity_id)
        assert loaded.created_at is not None
        assert loaded.updated_at is not None


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------


class TestList:
    def test_list_empty(self):
        result = list_entitymentions()
        assert result == []

    def test_list_all(self, sample_mention, mention_with_embedding):
        save_entitymention(sample_mention)
        save_entitymention(mention_with_embedding)
        result = list_entitymentions()
        assert len(result) == 2

    def test_list_by_cluster_id(self, mention_with_cluster, sample_mention):
        save_entitymention(mention_with_cluster)
        save_entitymention(sample_mention)
        result = list_entitymentions(cluster_id="a" * 64)
        assert len(result) == 1
        assert result[0].entity_id == mention_with_cluster.entity_id

    def test_list_by_nonexistent_cluster(self, sample_mention):
        save_entitymention(sample_mention)
        result = list_entitymentions(cluster_id="b" * 64)
        assert result == []


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------


class TestDelete:
    def test_delete_existing(self, sample_mention):
        save_entitymention(sample_mention)
        assert delete_entitymention(sample_mention.entity_id) is True
        assert get_entitymention(sample_mention.entity_id) is None

    def test_delete_nonexistent_returns_false(self):
        assert delete_entitymention("f" * 64) is False


# ---------------------------------------------------------------------------
# Embedding round-trip
# ---------------------------------------------------------------------------


class TestEmbedding:
    def test_empty_embedding_round_trip(self, sample_mention):
        """Mentions without embeddings should round-trip as empty list."""
        save_entitymention(sample_mention)
        loaded = get_entitymention(sample_mention.entity_id)
        assert loaded.embedding == []

    def test_full_embedding_round_trip(self, mention_with_embedding):
        """768-dim embeddings should survive a save/load cycle."""
        save_entitymention(mention_with_embedding)
        loaded = get_entitymention(mention_with_embedding.entity_id)
        assert len(loaded.embedding) == 768
        assert loaded.embedding[0] == pytest.approx(0.1)
        assert loaded.embedding[-1] == pytest.approx(0.1)


# ---------------------------------------------------------------------------
# Clustering fields round-trip
# ---------------------------------------------------------------------------


class TestClusteringFields:
    def test_cluster_fields_round_trip(self, mention_with_cluster):
        save_entitymention(mention_with_cluster)
        loaded = get_entitymention(mention_with_cluster.entity_id)
        assert loaded.cluster_id == "a" * 64
        assert loaded.similarity_score == pytest.approx(0.95)
        assert loaded.confidence_score == pytest.approx(0.88)
        assert loaded.is_medoid is True

    def test_default_cluster_fields(self, sample_mention):
        """Mentions without clustering should have default values."""
        save_entitymention(sample_mention)
        loaded = get_entitymention(sample_mention.entity_id)
        assert loaded.cluster_id == ""
        assert loaded.similarity_score == 0.0
        assert loaded.confidence_score == 0.0
        assert loaded.is_medoid is False
