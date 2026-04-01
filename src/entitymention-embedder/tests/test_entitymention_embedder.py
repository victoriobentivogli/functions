"""Tests for entitymention_embedder.py"""

import pytest
from entitymention import EntityMention
from entitymention_embedder import entitymention_embedder


@pytest.fixture
def sample_mention():
    """A cleaned EntityMention ready for embedding."""
    return EntityMention(
        origin_id="test-origin",
        request_id="test-request",
        entity_type="http://www.w3.org/ns/org/Organization",
        original_asset="http://example.org/Organization/ORG-0001",
        properties={
            "hasLegalName": "FORSYNING HELSINGØR A/S",
            "hasPrimaryContactPoint.email": "cnor@servia.dk",
        },
    )


class TestEntityMentionEmbedder:
    def test_returns_entitymention(self, sample_mention):
        """Embedder must return an EntityMention instance."""
        with pytest.raises(NotImplementedError):
            entitymention_embedder(sample_mention)

    def test_accepts_property_weights(self, sample_mention):
        """Embedder must accept optional property_weights parameter."""
        with pytest.raises(NotImplementedError):
            entitymention_embedder(
                sample_mention,
                property_weights={"hasLegalName": 0.6},
            )

    def test_preserves_properties(self, sample_mention):
        """Embedding must not alter the properties dict."""
        with pytest.raises(NotImplementedError):
            entitymention_embedder(sample_mention)
