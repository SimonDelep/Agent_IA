"""Tests du client HTTP MCP (sans serveur MCP stdio)."""

import json
from unittest.mock import MagicMock, patch

import httpx

from mcp_server import api_client


@patch("mcp_server.api_client.httpx.Client")
def test_request_success(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value.__enter__.return_value = mock_client
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"order_id": "NTG-2026-000201", "status": "livree"}
    mock_client.request.return_value = mock_response

    result = json.loads(api_client.request("GET", "/orders/NTG-2026-000201"))
    assert result["status"] == "livree"


@patch("mcp_server.api_client.httpx.Client")
def test_request_api_error(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value.__enter__.return_value = mock_client
    mock_response = MagicMock()
    mock_response.status_code = 409
    mock_response.json.return_value = {"detail": "Annulation impossible."}
    mock_client.request.return_value = mock_response

    result = json.loads(api_client.request("POST", "/orders/X/cancel"))
    assert result["error"] is True
    assert result["status"] == 409


@patch("mcp_server.api_client.httpx.Client")
def test_request_connection_error(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value.__enter__.return_value = mock_client
    mock_client.request.side_effect = httpx.ConnectError("refused")

    result = json.loads(api_client.request("GET", "/health"))
    assert result["error"] is True
    assert "API non joignable" in result["detail"]
