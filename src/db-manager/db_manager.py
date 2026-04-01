"""
db_manager.py
-------------
Database operations for EntityMention persistence in the Entity Resolution
Engine (ERE).

Uses PostgreSQL with pgvector for vector storage and similarity search.
Provides CRUD functions for storing, retrieving, listing, and deleting
EntityMention instances.
"""

from __future__ import annotations

import json
import os

import psycopg
from pgvector.psycopg import register_vector

from entitymention import EntityMention

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://ere:ere@localhost:5433/ere",
)


def _get_connection() -> psycopg.Connection:
    """Open a connection and register the pgvector type."""
    conn = psycopg.connect(DATABASE_URL, autocommit=True)
    register_vector(conn)
    return conn


def _row_to_entitymention(row: dict) -> EntityMention:
    """Convert a database row (dict) to an EntityMention instance."""
    properties = row["properties"] if isinstance(row["properties"], dict) else json.loads(row["properties"])
    embedding = list(row["embedding"]) if row["embedding"] is not None else []
    cluster_id = row["cluster_id"].strip() if row["cluster_id"] else ""

    return EntityMention(
        origin_id=row["origin_id"],
        request_id=row["request_id"],
        entity_type=row["entity_type"],
        entity_id=row["entity_id"].strip(),
        original_asset=row["original_asset"],
        properties=properties,
        embedding=embedding,
        cluster_id=cluster_id,
        similarity_score=row["similarity_score"],
        confidence_score=row["confidence_score"],
        is_medoid=row["is_medoid"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def save_entitymention(mention: EntityMention) -> EntityMention:
    """
    Persist an EntityMention to the database (upsert).

    If an entity mention with the same ``entity_id`` already exists, it is
    updated; otherwise a new record is created.

    Parameters
    ----------
    mention : EntityMention
        The entity mention to save.

    Returns
    -------
    EntityMention
        The saved instance as read back from the database.
    """
    embedding_val = mention.embedding if mention.embedding else None
    cluster_id_val = mention.cluster_id if mention.cluster_id else None
    properties_json = json.dumps(mention.properties)

    sql = """
        INSERT INTO entity_mentions (
            entity_id, origin_id, request_id, entity_type, original_asset,
            properties, embedding, cluster_id,
            similarity_score, confidence_score, is_medoid,
            created_at, updated_at
        ) VALUES (
            %(entity_id)s, %(origin_id)s, %(request_id)s, %(entity_type)s,
            %(original_asset)s, %(properties)s::jsonb, %(embedding)s, %(cluster_id)s,
            %(similarity_score)s, %(confidence_score)s, %(is_medoid)s,
            %(created_at)s, %(updated_at)s
        )
        ON CONFLICT (entity_id) DO UPDATE SET
            origin_id        = EXCLUDED.origin_id,
            request_id       = EXCLUDED.request_id,
            entity_type      = EXCLUDED.entity_type,
            original_asset   = EXCLUDED.original_asset,
            properties       = EXCLUDED.properties,
            embedding        = EXCLUDED.embedding,
            cluster_id       = EXCLUDED.cluster_id,
            similarity_score = EXCLUDED.similarity_score,
            confidence_score = EXCLUDED.confidence_score,
            is_medoid        = EXCLUDED.is_medoid,
            updated_at       = EXCLUDED.updated_at
    """

    params = {
        "entity_id": mention.entity_id,
        "origin_id": mention.origin_id,
        "request_id": mention.request_id,
        "entity_type": mention.entity_type,
        "original_asset": mention.original_asset,
        "properties": properties_json,
        "embedding": embedding_val,
        "cluster_id": cluster_id_val,
        "similarity_score": mention.similarity_score,
        "confidence_score": mention.confidence_score,
        "is_medoid": mention.is_medoid,
        "created_at": mention.created_at,
        "updated_at": mention.updated_at,
    }

    with _get_connection() as conn:
        conn.execute(sql, params)

    return get_entitymention(mention.entity_id)


def get_entitymention(entity_id: str) -> EntityMention | None:
    """
    Retrieve a single EntityMention by its entity_id.

    Parameters
    ----------
    entity_id : str
        The SHA256 identifier of the entity mention to retrieve.

    Returns
    -------
    EntityMention or None
        The matching entity mention, or ``None`` if not found.
    """
    sql = "SELECT * FROM entity_mentions WHERE entity_id = %(entity_id)s"

    with _get_connection() as conn:
        cur = conn.execute(sql, {"entity_id": entity_id})
        row = cur.fetchone()

    if row is None:
        return None

    columns = [desc.name for desc in cur.description]
    row_dict = dict(zip(columns, row))
    return _row_to_entitymention(row_dict)


def list_entitymentions(
    cluster_id: str | None = None,
) -> list[EntityMention]:
    """
    List EntityMention instances, optionally filtered by cluster.

    Parameters
    ----------
    cluster_id : str or None
        When provided, only entity mentions belonging to this cluster are
        returned.  When ``None`` (default), all entity mentions are returned.

    Returns
    -------
    list[EntityMention]
        A list of matching entity mentions.
    """
    if cluster_id is not None:
        sql = "SELECT * FROM entity_mentions WHERE cluster_id = %(cluster_id)s ORDER BY created_at"
        params = {"cluster_id": cluster_id}
    else:
        sql = "SELECT * FROM entity_mentions ORDER BY created_at"
        params = {}

    with _get_connection() as conn:
        cur = conn.execute(sql, params)
        rows = cur.fetchall()

    if not rows:
        return []

    columns = [desc.name for desc in cur.description]
    return [_row_to_entitymention(dict(zip(columns, row))) for row in rows]


def delete_entitymention(entity_id: str) -> bool:
    """
    Delete an EntityMention by its entity_id.

    Parameters
    ----------
    entity_id : str
        The SHA256 identifier of the entity mention to delete.

    Returns
    -------
    bool
        ``True`` if the entity mention was found and deleted, ``False``
        otherwise.
    """
    sql = "DELETE FROM entity_mentions WHERE entity_id = %(entity_id)s"

    with _get_connection() as conn:
        cur = conn.execute(sql, {"entity_id": entity_id})
        return cur.rowcount > 0
