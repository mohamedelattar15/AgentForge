# AgentForge — Tests DeepEval Eval

import pytest
from unittest.mock import MagicMock, patch

from agentforge_deepeval import DeepEvalEval


@pytest.fixture
def adapter():
    """Fixture retournant un évaluateur DeepEval."""
    return DeepEvalEval(metrics=["answer_relevancy"], threshold=0.7)


class TestDeepEvalEval:
    """Tests pour DeepEvalEval (mocké)."""

    @pytest.mark.asyncio
    async def test_evaluate_no_metrics(self):
        """evaluate() sans métriques doit retourner parfait."""
        adapter = DeepEvalEval(metrics=[])
        result = await adapter.evaluate({"messages": []})
        assert result.passed is True
        assert result.score == 1.0

    @pytest.mark.asyncio
    async def test_evaluate_missing_question(self):
        """evaluate() sans question doit retourner parfait (mode dégradé)."""
        adapter = DeepEvalEval(metrics=["answer_relevancy"], threshold=0.7)
        result = await adapter.evaluate({"messages": []})
        assert result.passed is True
        assert result.score == 1.0

    def test_extract_answer(self, adapter):
        """_extract_answer() doit trouver la dernière réponse."""
        messages = [
            {"role": "user", "content": "Question"},
            {"role": "assistant", "content": "Réponse"},
        ]
        answer = adapter._extract_answer(messages)
        assert answer == "Réponse"

    def test_extract_answer_empty(self, adapter):
        """_extract_answer() sans assistant doit retourner ''."""
        answer = adapter._extract_answer([])
        assert answer == ""

    def test_lazy_init_empty_metrics(self):
        """_lazy_init() avec metrics=[] ne doit pas créer de métriques."""
        adapter = DeepEvalEval(metrics=[])  # nouvelle instance, pas de contamination
        adapter._lazy_init()
        assert adapter._metrics == []  # toujours vide car pas de noms de métriques

    def test_lazy_init_with_metrics_no_api_key(self):
        """_lazy_init() sans clé API doit mettre un marqueur."""
        adapter = DeepEvalEval(metrics=["answer_relevancy"])
        adapter._lazy_init()
        # En l'absence de clé API OpenAI, lazy_init met un marqueur
        assert adapter._metrics == ["lazy"]
