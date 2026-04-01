"""
entitymention_clusterer.py
--------------------------
Calculates clusters from a collection of EntityMention instances based on
their embeddings.

This is the final analytical stage of the ERE pipeline.  It receives a list
of EntityMentions (with embeddings populated by the entitymention-embedder)
and returns updated instances with clustering fields filled via
``mention.update_record()``.
"""

from __future__ import annotations

from entitymention import EntityMention


def entitymention_clusterer(
    mentions: list[EntityMention],
) -> list[EntityMention]:
    """
    Assign cluster memberships to a list of entity mentions.

    Groups entity mentions by similarity of their embedding vectors, then
    assigns each mention a ``cluster_id``, ``similarity_score``,
    ``confidence_score``, and ``is_medoid`` flag.

    Parameters
    ----------
    mentions : list[EntityMention]
        Entity mentions with ``embedding`` populated (typically by the
        entitymention-embedder).

    Returns
    -------
    list[EntityMention]
        New frozen instances with clustering fields set and refreshed
        ``updated_at`` timestamps.

    Raises
    ------
    NotImplementedError
        This function is a stub awaiting implementation.
    """
    raise NotImplementedError("entitymention_clusterer is not yet implemented")
