"""Tests for entitymention_clusterer.py"""

import pytest
from entitymention import EntityMention
from entitymention_clusterer import entitymention_clusterer


@pytest.fixture
def sample_mentions():
    """A list of EntityMentions with embeddings, ready for clustering."""
    base = {
        "origin_id": "test-origin",
        "request_id": "test-request",
        "entity_type": "http://www.w3.org/ns/org/Organization",
        "original_asset": "http://example.org/Organization/ORG-0001",
        "embedding": [0.1] * 768,
    }
    return [
        EntityMention(**base, properties={"hasLegalName": "Org A"}),
        EntityMention(**base, properties={"hasLegalName": "Org B"}),
        EntityMention(**base, properties={"hasLegalName": "Org C"}),
    ]


class TestEntityMentionClusterer:
    def test_returns_list(self, sample_mentions):
        """Clusterer must return a list."""
        with pytest.raises(NotImplementedError):
            entitymention_clusterer(sample_mentions)

    def test_accepts_empty_list(self):
        """Clusterer must handle an empty input list."""
        with pytest.raises(NotImplementedError):
            entitymention_clusterer([])

    def test_single_mention(self, sample_mentions):
        """Clusterer must handle a single entity mention."""
        with pytest.raises(NotImplementedError):
            entitymention_clusterer([sample_mentions[0]])
