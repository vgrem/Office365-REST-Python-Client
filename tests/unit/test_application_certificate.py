"""Offline tests for ``Application.ensure_certificate`` / ``add_certificate``.

Covers the certificate normalisation helpers (DER/PEM bytes, PEM text and file
paths), the SHA-1 thumbprint form Entra stores in ``customKeyIdentifier``, and
the idempotent ``ensure_certificate`` request shape: it must skip the update
when the certificate is already attached and PATCH the app otherwise.
"""

from __future__ import annotations

import base64
import ssl

from office365.directory.applications.application import (
    Application,
    _certificate_der,
)
from office365.graph_client import GraphClient
from office365.runtime.http.http_method import HttpMethod
from tests._scripted_transport import RoutingTransport

APP_ID = "11111111-1111-1111-1111-111111111111"
# Arbitrary bytes: the helpers treat anything without a PEM header as DER, so no
# real certificate is needed to exercise the thumbprint/tagging logic.
DER = bytes.fromhex("3082010a0282010100deadbeefcafe1234")


def _client(transport: RoutingTransport) -> GraphClient:
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    client.pending_request().transport = transport
    return client


def _app(client: GraphClient) -> Application:
    return client.applications.get_by_app_id(APP_ID)


def _key_credentials_response(*identifiers: str) -> dict:
    return {
        "keyCredentials": [
            {"customKeyIdentifier": identifier, "type": "AsymmetricX509Cert", "usage": "Verify"}
            for identifier in identifiers
        ]
    }


def test_certificate_der_accepts_pem_bytes_and_path(tmp_path):
    pem = ssl.DER_cert_to_PEM_cert(DER)

    assert _certificate_der(DER) == DER  # type: ignore[arg-type]
    assert _certificate_der(pem) == DER
    assert _certificate_der(pem.encode("utf-8")) == DER

    cert_path = tmp_path / "cert.crt"
    cert_path.write_text(pem, encoding="utf-8")
    assert _certificate_der(cert_path) == DER


def test_ensure_certificate_skips_update_when_already_attached():
    thumbprint = Application.certificate_thumbprint(DER)  # type: ignore[arg-type]
    transport = RoutingTransport(
        [
            ("keyCredentials", _key_credentials_response(thumbprint)),
            ("applications", {}),
        ]
    )
    client = _client(transport)

    _app(client).ensure_certificate(DER, "test-cert").execute_query()  # type: ignore[arg-type]

    assert [r.method for r in transport.requests] == [HttpMethod.Get]


def test_ensure_certificate_attaches_when_missing():
    transport = RoutingTransport(
        [
            ("keyCredentials", _key_credentials_response("AABBCCDD")),
            ("applications", {}),
        ]
    )
    client = _client(transport)

    _app(client).ensure_certificate(DER, "test-cert").execute_query()  # type: ignore[arg-type]

    updates = [r for r in transport.requests if r.method == HttpMethod.Patch]
    assert len(updates) == 1
    credentials = updates[0].data["keyCredentials"]
    added = next(c for c in credentials if c.get("displayName") == "CN=test-cert")
    assert added["key"] == base64.b64encode(DER).decode("utf-8")
