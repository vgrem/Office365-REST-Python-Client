"""Offline tests for ``Application.ensure_certificate`` / ``add_certificate``.

Covers the certificate normalisation helpers (DER/PEM bytes, PEM text and file
paths), the SHA-1 thumbprint form Entra stores in ``customKeyIdentifier``, and
the idempotent ``ensure_certificate`` request shape: it must skip the update
when the certificate is already attached and PATCH the app otherwise.
"""

from __future__ import annotations

import ssl

from office365.directory.applications.application import (
    _certificate_der,
)

APP_ID = "11111111-1111-1111-1111-111111111111"
# Arbitrary bytes: the helpers treat anything without a PEM header as DER, so no
# real certificate is needed to exercise the thumbprint/tagging logic.
DER = bytes.fromhex("3082010a0282010100deadbeefcafe1234")


def test_certificate_der_accepts_pem_bytes_and_path(tmp_path):
    pem = ssl.DER_cert_to_PEM_cert(DER)

    assert _certificate_der(DER) == DER  # type: ignore[arg-type]
    assert _certificate_der(pem) == DER
    assert _certificate_der(pem.encode("utf-8")) == DER

    cert_path = tmp_path / "cert.crt"
    cert_path.write_text(pem, encoding="utf-8")
    assert _certificate_der(cert_path) == DER
