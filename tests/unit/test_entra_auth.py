"""Tests for the Entra (Graph) authentication context device flow (offline)."""

from __future__ import annotations

import sys
import types

from office365.runtime.auth.entra.authentication_context import AuthenticationContext


class _FakePublicClientApplication:
    """Minimal MSAL stand-in that records device-flow / silent acquisition calls."""

    def __init__(self, client_id, authority=None, **kwargs):
        self.accounts: list[dict] = []
        self.silent_result: dict | None = {"access_token": "cached"}
        self.initiated = 0
        self.silent_calls = 0

    def get_accounts(self, username=None):
        return list(self.accounts)

    def acquire_token_silent(self, scopes, account=None, **kwargs):
        self.silent_calls += 1
        return self.silent_result

    def initiate_device_flow(self, scopes=None, **kwargs):
        self.initiated += 1
        return {"user_code": "ABCD", "message": "visit https://microsoft.com/devicelogin and enter ABCD"}

    def acquire_token_by_device_flow(self, flow):
        self.accounts.append({"home_account_id": "account-1"})
        return {"access_token": "device", "expires_in": 3600}


def _install_fake_msal(monkeypatch) -> list[_FakePublicClientApplication]:
    created: list[_FakePublicClientApplication] = []

    def _factory(*args, **kwargs):
        app = _FakePublicClientApplication(*args, **kwargs)
        created.append(app)
        return app

    fake = types.ModuleType("msal")
    fake.PublicClientApplication = _factory  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "msal", fake)
    return created


def test_device_flow_prompts_once_then_reuses_cached_token(monkeypatch):
    created = _install_fake_msal(monkeypatch)
    ctx = AuthenticationContext(tenant="contoso.onmicrosoft.com")
    ctx.with_device_flow("client-id")
    acquire = ctx._token_callback
    assert acquire is not None

    assert acquire()["access_token"] == "device"
    assert acquire()["access_token"] == "cached"

    app = created[0]
    assert app.initiated == 1
    assert app.silent_calls == 1
