"""
entitymention_embedder.py
-------------------------
Calculates embeddings for an EntityMention based on its properties,
combines them according to given weights, and adjusts their scale.

This is the third stage of the ERE pipeline.  It receives a cleaned
EntityMention and returns a new instance with the ``embedding`` field
populated (768-dimension vector) via ``mention.update_record()``.
"""

from __future__ import annotations

from entitymention import EntityMention


def entitymention_embedder(
    mention: EntityMention,
    property_weights: dict[str, float] | None = None,
) -> EntityMention:
    """
    Calculate and attach an embedding vector to an entity mention.

    Generates embeddings from the mention's properties, optionally weighting
    each property's contribution according to *property_weights*.  The
    resulting 768-dimension vector is stored in the ``embedding`` field.

    Parameters
    ----------
    mention : EntityMention
        The entity mention to embed.  Must have ``properties`` populated
        (typically cleaned by the entitymention-cleaner).
    property_weights : dict[str, float] or None
        Optional mapping of property names to their relative weights in
        the combined embedding.  When ``None`` (default), all properties
        contribute equally.

    Returns
    -------
    EntityMention
        A new frozen instance with the ``embedding`` field set and a
        refreshed ``updated_at`` timestamp.

    Raises
    ------
    NotImplementedError
        This function is a stub awaiting implementation.
    """
    raise NotImplementedError("entitymention_embedder is not yet implemented")
