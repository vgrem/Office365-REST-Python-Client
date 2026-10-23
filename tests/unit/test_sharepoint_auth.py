"""Tests for SharePoint client-context authentication wiring (offline)."""

from __future__ import annotations

import pytest
import requests
from office365.runtime.http.request_options import RequestOptions
from office365.sharepoint.client_context import ClientContext


def test_with_user_credentials_uses_ntlm_when_allowed(monkeypatch):
    monkeypatch.setattr(
        "office365.runtime.auth.providers.ntlm_provider.NtlmProvider.__init__",
        lambda self, credentials, *args, **kwargs: None,
    )
    ctx = ClientContext("https://sp2019.contoso.local", allow_ntlm=True)

    ctx.with_user_credentials("DOMAIN\\user", "pwd")  # must not raise

    assert callable(ctx.authentication_context._authenticate)


def test_custom_session_without_auth_still_raises():
    ctx = ClientContext("https://sp2019.contoso.local").with_transport(session=requests.Session())

    request = RequestOptions("https://sp2019.contoso.local/_api/web")
    with pytest.raises(ValueError, match="missing or invalid"):
        ctx.pending_request()._authenticate_request(request)


def test_configured_credentials_win_over_session_auth(monkeypatch):
    monkeypatch.setattr(
        "office365.runtime.auth.providers.ntlm_provider.NtlmProvider.__init__",
        lambda self, credentials, *args, **kwargs: None,
    )
    monkeypatch.setattr(
        "office365.runtime.auth.providers.ntlm_provider.NtlmProvider.authenticate_request",
        lambda self, request: request.set_header("X-From-Provider", "1"),
    )
    session = requests.Session()
    session.auth = requests.auth.HTTPBasicAuth("DOMAIN\\user", "pwd")
    ctx = ClientContext("https://sp2019.contoso.local", allow_ntlm=True).with_transport(session=session)
    ctx.with_user_credentials("DOMAIN\\user", "pwd")

    request = RequestOptions("https://sp2019.contoso.local/_api/web")
    ctx.pending_request()._authenticate_request(request)

    assert request.headers["X-From-Provider"] == "1"
