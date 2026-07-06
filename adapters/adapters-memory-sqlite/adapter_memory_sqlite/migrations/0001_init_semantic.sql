-- AgentForge — Migration SQLite 001
-- Table pour la mémoire sémantique

CREATE TABLE IF NOT EXISTS semantic_facts (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    metadata TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
