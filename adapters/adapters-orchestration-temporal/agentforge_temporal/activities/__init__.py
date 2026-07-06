# AgentForge — Activités Temporal pour l'agent

from temporalio import activity


@activity.defn
async def plan_activity(user_query: str) -> list[str]:
    """Activité de planification.

    Args:
        user_query: Requête utilisateur.

    Returns:
        list[str]: Liste des étapes planifiées.
    """
    return ["analyser", "répondre"]


@activity.defn
async def execute_activity(payload: dict) -> str:
    """Activité d'exécution d'une étape.

    Args:
        payload: Contient 'step' et 'messages'.

    Returns:
        str: Résultat de l'étape.
    """
    step = payload.get("step", "")
    return f"Étape '{step}' exécutée."


@activity.defn
async def llm_activity(messages: list[dict]) -> str:
    """Activité d'appel LLM.

    Args:
        messages: Messages formatés.

    Returns:
        str: Réponse du LLM.
    """
    return "Réponse générée par le LLM."


@activity.defn
async def memory_activity(action: str, data: dict) -> str:
    """Activité mémoire.

    Args:
        action: Type d'action (save, load, search).
        data: Données associées.

    Returns:
        str: Résultat de l'opération mémoire.
    """
    return f"Mémoire : {action} effectué."


@activity.defn
async def tool_activity(tool_name: str, args: dict) -> str:
    """Activité d'exécution d'outil.

    Args:
        tool_name: Nom de l'outil.
        args: Arguments d'appel.

    Returns:
        str: Résultat de l'outil.
    """
    return f"Outil '{tool_name}' exécuté."
