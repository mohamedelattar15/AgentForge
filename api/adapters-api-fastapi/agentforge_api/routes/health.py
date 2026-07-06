# AgentForge — API FastAPI : endpoint /health

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health():
    """Endpoint de health check.

    Returns:
        dict: Statut et version de l'API.
    """
    return {"status": "ok", "version": "0.2.0"}
