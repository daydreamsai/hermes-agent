from hermes_cli import runtime_provider as rp
from hermes_cli.auth import ProviderConfig


def test_resolve_runtime_provider_includes_payment_runtime(monkeypatch):
    monkeypatch.setattr(rp, "resolve_provider", lambda *a, **k: "paid-provider")
    monkeypatch.setitem(
        rp.PROVIDER_REGISTRY,
        "paid-provider",
        ProviderConfig(
            id="paid-provider",
            name="Paid Provider",
            auth_type="api_key",
            inference_base_url="https://paid.example/v1",
            api_key_env_vars=("PAID_PROVIDER_API_KEY",),
        ),
    )
    monkeypatch.setattr(
        rp,
        "resolve_api_key_provider_credentials",
        lambda provider: {
            "provider": provider,
            "base_url": "https://paid.example/v1",
            "api_key": "paid-key",
            "source": "env",
            "payment_adapter": "mpp",
            "payment_config": {"method": "test-method"},
        },
    )

    resolved = rp.resolve_runtime_provider(requested="paid-provider")

    assert resolved["provider"] == "paid-provider"
    assert resolved["payment_adapter"] == "mpp"
    assert resolved["payment_config"] == {"method": "test-method"}
