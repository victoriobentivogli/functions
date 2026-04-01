"""
entitymention.py
---------
Shared Pydantic model for entity mentions flowing through the Entity Resolution Engine (ERE).
"""

import hashlib
import datetime
import re
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, model_validator, field_validator

SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")

class EntityMention(BaseModel):
    """
    A single entity mention representation. This is the primary data structure used to represent entity mentions as they flow 
    through the ERE.
    Each EntityMention instance corresponds to a single mention of an entity with its properties.
    This representation is designed to be flexible and extensible, allowing for the inclusion of various metadata and tracking
    information as needed.

    Attributes
    ----------
    origin_id : str
        A unique identifier for the origin of this entity mention, used for tracking.
    request_id : str
        A unique identifier for the request assigned by the client, used for tracking
    entity_type : str
        The type (i.e.: )``rdf:type`` URI) of the entity mention.

    entity_id : str
        A unique identifier for this entity mention, calculated on the value of a subset of the properties.

    original_asset : str
        The original asset to which this entity mention corresponds.

    properties : dict[str, str | list[str]]
        Flat property map.  Nested RDF references are represented with
        dot-notation keys (e.g. ``hasPrimaryContactPoint.email``).
        Multi-valued predicates produce a ``list[str]`` value.

    embedding: list[float]
        Embedding vector for this entity mention, used for similarity calculations.
    cluster_id : str
        Identifier for the cluster this entity mention belongs to, used for grouping similar entities.  
    similarity_score : float
        Similarity score to a reference entity mention, used for clustering and deduplication.
    confidence_score : float
        Confidence score for the entity mention's properties, used for filtering and ranking.
    is_medoid : bool
        Flag indicating whether this entity mention is a medoid (representative) of a cluster of similar entities.

    created_at : datetime
        Timestamp for when this entity mention was created, used for tracking and auditing.
    updated_at : datetime
        Timestamp for when this entity mention was last updated, used for tracking and auditing.
    """

    model_config = ConfigDict(frozen=True)

    # Identification
    origin_id: str
    request_id: str
    entity_type: str

    entity_id: str = "" 
    
    # Original data
    original_asset: str
    
    # Data & ML
    properties: dict[str, str | list[str]]
    embedding: list[float] = Field(default_factory=list)
    cluster_id: str = ""
    similarity_score: float = 0.0
    confidence_score: float = 0.0
    is_medoid: bool = False

    # Audit
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)

    @field_validator("embedding", mode="after")
    @classmethod
    def validate_embedding(cls, v: list[float]) -> list[float]:
        if len(v) != 0 and len(v) != 768:
            raise ValueError("Embedding must be empty or have exactly 768 elements")
        return v

    @field_validator("entity_id", "cluster_id", mode="after")
    @classmethod
    def validate_sha256(cls, v: str) -> str:
        if v == "": return v # Allow empty during init for entity_id
        if not SHA256_PATTERN.match(v):
            raise ValueError("Must be a 64-character SHA256 hex string")
        return v

    @model_validator(mode="after")
    def compute_fields(self) -> "EntityMention":
        if not self.entity_id:
            raw = f"{self.origin_id}:{self.request_id}:{self.entity_type}"
            hash_val = hashlib.sha256(raw.encode("utf-8")).hexdigest()
            object.__setattr__(self, "entity_id", hash_val)
        return self

    def update_record(self, **changes: Any) -> "EntityMention":
        """
        Derives a new version of the mention.
        If cluster_id changes, is_medoid is defaulted to False unless specified.
        """
        # Auto-refresh timestamp
        changes["updated_at"] = datetime.datetime.now()
        
        # Logic: If moving to a new cluster, it's likely no longer the medoid
        if "cluster_id" in changes and changes["cluster_id"] != self.cluster_id:
            changes.setdefault("is_medoid", False)
            
        return self.model_copy(update=changes)