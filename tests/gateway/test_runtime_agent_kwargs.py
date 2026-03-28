import importlib


def test_resolve_runtime_agent_kwargs_includes_payment_runtime(monkeypatch):
    gateway_run = importlib.import_module("gateway.run")

    monkeypatch.setattr(
        "hermes_cli.runtime_provider.resolve_runtime_provider",
        lambda **kwargs: {
            "api_key": "paid-key",
            "base_url": "https://paid.example/v1",
            "provider": "paid-provider",
            "api_mode": "chat_completions",
            "request_headers_resolver": None,
            "payment_adapter": "mpp",
            "payment_config": {"method": "test-method"},
        },
    )
    monkeypatch.setattr(
        "hermes_cli.runtime_provider.format_runtime_provider_error",
        lambda exc: str(exc),
    )

    result = gateway_run._resolve_runtime_agent_kwargs()

    assert result["payment_adapter"] == "mpp"
    assert result["payment_config"] == {"method": "test-method"}
