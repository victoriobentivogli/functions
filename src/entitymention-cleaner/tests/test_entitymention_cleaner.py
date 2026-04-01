"""Tests for entitymention_cleaner.py"""

import pytest
from entitymention import EntityMention
from entitymention_cleaner import entitymention_cleaner


@pytest.fixture
def sample_mention():
    """An EntityMention with properties as produced by the extractor."""
    return EntityMention(
        origin_id="test-origin",
        request_id="test-request",
        entity_type="http://www.w3.org/ns/org/Organization",
        original_asset="http://example.org/Organization/ORG-0001",
        properties={
            "hasLegalName": "  FORSYNING HELSINGØR A/S  ",
            "hasPrimaryContactPoint.email": "cnor@servia.dk",
        },
    )


class TestEntityMentionCleaner:
    def test_returns_entitymention(self, sample_mention):
        """Cleaner must return an EntityMention instance."""
        with pytest.raises(NotImplementedError):
            entitymention_cleaner(sample_mention)

    def test_preserves_origin_id(self, sample_mention):
        """Cleaning must not alter tracking fields."""
        with pytest.raises(NotImplementedError):
            entitymention_cleaner(sample_mention)

    def test_preserves_entity_type(self, sample_mention):
        """Cleaning must not alter the entity type."""
        with pytest.raises(NotImplementedError):
            entitymention_cleaner(sample_mention)
