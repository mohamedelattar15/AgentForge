# AgentForge — Tests Ragas Eval

import pytest
from unittest.mock import MagicMock, patch

from agentforge_core.types import EvalResult
from agentforge_ragas import RagasEval


class TestRagasEval:
    """Tests pour RagasEval (mocké)."""

    @pytest.fixture
    def adapter(self):
        """Fixture retournant un évaluateur Ragas."""
        return RagasEval(metrics=["faithfulness"], threshold=0.7)

    @pytest.mark.asyncio
    async def test_evaluate_no_metrics(self):
        """evaluate() sans métriques doit retourner parfait."""
        with patch.object(RagasEval, "AVAILABLE_METRICS", {}):
            adapter = RagasEval(metrics=[])
            result = await adapter.evaluate({"messages": []})
            assert result.passed is True
            assert result.score == 1.0

    @pytest.mark.asyncio
    async def test_evaluate_missing_question(self, adapter):
        """evaluate() sans question doit échouer."""
        result = await adapter.evaluate({"messages": []})
        assert result.passed is False
        assert result.score == 0.0

    @pytest.mark.asyncio
    async def test_extract_answer_from_dict(self, adapter):
        """_extract_answer() doit trouver la dernière réponse assistant."""
        messages = [
            {"role": "user", "content": "Question"},
            {"role": "assistant", "content": "Réponse finale"},
        ]
        answer = adapter._extract_answer(messages)
        assert answer == "Réponse finale"

    @pytest.mark.asyncio
    async def test_extract_answer_empty(self, adapter):
        """_extract_answer() sans assistant doit retourner ''."""
        messages = [{"role": "user", "content": "Question"}]
        answer = adapter._extract_answer(messages)
        assert answer == ""

    def test_extract_contexts(self, adapter):
        """_extract_contexts() doit extraire les faits."""
        trace = {
            "working_memory": {
                "semantic_facts": [
                    {"content": "Fait 1"},
                    {"content": "Fait 2"},
                ]
            }
        }
        contexts = adapter._extract_contexts(trace)
        assert contexts == ["Fait 1", "Fait 2"]

    def test_extract_contexts_empty(self, adapter):
        """_extract_contexts() sans faits doit retourner []."""
        contexts = adapter._extract_contexts({})
        assert contexts == []
