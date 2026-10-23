"""Offline tests for the certificate authentication helpers.

Covers ``office365.runtime.auth.certificate``: normalising DER/PEM bytes, inline
PEM text and file paths, the SHA-1 thumbprint Entra stores, and the MSAL
``client_credential`` built for legacy thumbprint vs subject name/issuer (SNI)
authentication.
"""

from __future__ import annotations

import ssl

import pytest
from office365.runtime.auth.certificate import (
    build_client_credential,
    certificate_pem,
    certificate_thumbprint,
)

# Arbitrary bytes: anything without a PEM header is treated as DER, so no real
# certificate is needed to exercise the normalisation/thumbprint logic.
DER = bytes.fromhex("3082010a0282010100deadbeefcafe1234")
PEM = ssl.DER_cert_to_PEM_cert(DER)


def test_build_client_credential_derives_thumbprint_from_public_certificate():
    credential = build_client_credential(private_key="KEY", public_certificate=PEM)
    assert credential["thumbprint"] == certificate_thumbprint(PEM)
    assert credential["private_key"] == "KEY"
    assert "public_certificate" not in credential


def test_build_client_credential_derives_thumbprint_from_path(tmp_path):
    cert_path = tmp_path / "cert.crt"
    cert_path.write_text(PEM, encoding="utf-8")
    credential = build_client_credential(private_key="KEY", public_certificate=cert_path)
    assert credential["thumbprint"] == certificate_thumbprint(DER)


def test_build_client_credential_sni_passes_public_certificate():
    pytest.importorskip("cryptography")
    credential = build_client_credential(private_key="KEY", public_certificate=PEM, use_sni=True)
    assert credential == {"private_key": "KEY", "public_certificate": PEM}
    assert "thumbprint" not in credential


def test_certificate_pem_round_trips_der_and_pem():
    assert certificate_pem(DER) == PEM
    assert certificate_pem(PEM) == PEM


def test_entra_with_certificate_derives_thumbprint(monkeypatch):
    import msal
    from office365.runtime.auth.entra.authentication_context import AuthenticationContext

    captured = {}

    class FakeConfidentialClientApplication:
        def __init__(self, client_id, authority, client_credential, token_cache=None):
            captured["client_id"] = client_id
            captured["credential"] = client_credential

    monkeypatch.setattr(msal, "ConfidentialClientApplication", FakeConfidentialClientApplication)
    context = AuthenticationContext(tenant="contoso.onmicrosoft.com")

    context.with_certificate("client-id", private_key="KEY", public_certificate=PEM)

    assert captured["client_id"] == "client-id"
    assert captured["credential"]["thumbprint"] == certificate_thumbprint(PEM)
