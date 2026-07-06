-- AgentForge — Migration SQLite 002
-- Table pour la mémoire épisodique

CREATE TABLE IF NOT EXISTS episodic_messages (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    tool_calls TEXT DEFAULT '[]',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_episodic_session
ON episodic_messages(session_id);
