-- AgentForge — Migration ClickHouse 001
-- Table de métriques d'exécution

CREATE TABLE IF NOT EXISTS run_metrics (
    run_id String,
    timestamp DateTime,
    agent_version String,
    user_query String,
    status String,
    latency_ms Float64,
    token_count UInt32,
    iteration_count UInt32,
    tool_call_count UInt32,
    eval_score Float64,
    llm_model String,
    session_id String,
    metadata String
) ENGINE = MergeTree()
ORDER BY (timestamp, run_id)
