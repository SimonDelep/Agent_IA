"""Client HTTP vers l'API NordTrail Gear."""

from __future__ import annotations

import json
from typing import Any

import httpx

from mcp_server.config import API_BASE_URL, REQUEST_TIMEOUT


def _format_response(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def _format_error(status: int, detail: str) -> str:
    return _format_response({"error": True, "status": status, "detail": detail})


def request(
    method: str,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    json_body: dict[str, Any] | None = None,
) -> str:
    """Exécute une requête API et renvoie du JSON texte pour le LLM."""
    url_path = path if path.startswith("/") else f"/{path}"
    try:
        with httpx.Client(
            base_url=API_BASE_URL, timeout=REQUEST_TIMEOUT
        ) as client:
            response = client.request(method, url_path, params=params, json=json_body)
    except httpx.ConnectError:
        return _format_error(
            0,
            "API non joignable. Démarrez l'API : "
            "cd Serveur_MCP && uvicorn api.main:app --port 8000",
        )
    except httpx.TimeoutException:
        return _format_error(0, "Délai d'attente API dépassé.")

    if response.status_code >= 400:
        try:
            payload = response.json()
            detail = payload.get("detail", payload)
        except ValueError:
            detail = response.text or response.reason_phrase
        if isinstance(detail, list):
            detail = json.dumps(detail, ensure_ascii=False)
        return _format_error(response.status_code, str(detail))

    if response.status_code == 204:
        return _format_response({"success": True, "message": "Opération réussie."})

    try:
        return _format_response(response.json())
    except ValueError:
        return _format_response({"raw": response.text})
