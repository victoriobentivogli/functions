-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- EntityMention table
CREATE TABLE IF NOT EXISTS entity_mentions (
    entity_id        CHAR(64) PRIMARY KEY,
    origin_id        TEXT NOT NULL,
    request_id       TEXT NOT NULL,
    entity_type      TEXT NOT NULL,
    original_asset   TEXT NOT NULL,
    properties       JSONB NOT NULL DEFAULT '{}',
    embedding        vector(768),
    cluster_id       CHAR(64),
    similarity_score DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    confidence_score DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    is_medoid        BOOLEAN NOT NULL DEFAULT FALSE,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
