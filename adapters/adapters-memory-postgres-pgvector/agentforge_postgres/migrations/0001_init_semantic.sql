-- AgentForge — Migration PostgreSQL 001
-- Table pour la mémoire sémantique (avec pgvector)

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS semantic_facts (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_semantic_embedding
ON semantic_facts
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
