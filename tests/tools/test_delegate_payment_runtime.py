from unittest.mock import MagicMock, patch

from tools.delegate_tool import _resolve_delegation_credentials


def _make_parent():
    parent = MagicMock()
    parent.base_url = "https://openrouter.ai/api/v1"
    parent.api_key = "parent-key"
    parent.provider = "openrouter"
    parent.api_mode = "chat_completions"
    parent.model = "anthropic/claude-sonnet-4"
    return parent


@patch("hermes_cli.runtime_provider.resolve_runtime_provider")
def test_delegation_credentials_include_payment_runtime(mock_resolve):
    mock_resolve.return_value = {
        "provider": "paid-provider",
        "base_url": "https://paid.example/v1",
        "api_key": "paid-key",
        "api_mode": "chat_completions",
        "payment_adapter": "mpp",
        "payment_config": {"method": "test-method"},
    }

    creds = _resolve_delegation_credentials(
        {"model": "paid-model", "provider": "paid-provider"},
        _make_parent(),
    )

    assert creds["payment_adapter"] == "mpp"
    assert creds["payment_config"] == {"method": "test-method"}
