"""
Renew an app's certificate *only if* it is expiring soon.

Checks the newest key credential first and does nothing when there is still
plenty of validity. By default a fresh self-signed pair is generated with
openssl; pass ``--cert`` to upload an existing certificate.

Usage:

    python renew_cert.py                       # renew when below 30 days
    python renew_cert.py --warn-days 45
    python renew_cert.py --cert /path/to/cert.crt

Requires an interactive sign-in by a Global Administrator or Privileged Role
Administrator (the delegated ``Application.ReadWrite.All`` scope is carried by
the signed-in account).

Reference:
    https://learn.microsoft.com/en-us/graph/api/application-addcertificate
"""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path

from office365.graph_client import GraphClient
from tests.settings import admin_username, client_id, tenant

DEFAULT_WARN_DAYS = 30


def _privileged_client() -> GraphClient:
    return (
        GraphClient(tenant=tenant)
        .with_token_interactive(client_id, admin_username)
        .require_role("Global Administrator", "Privileged Role Administrator")
    )


def _generate_certificate(directory: Path, common_name: str) -> tuple[Path, Path]:
    key_path, cert_path = directory / "private.pem", directory / "public.crt"
    subprocess.run(["openssl", "genrsa", "-out", str(key_path), "2048"], check=True, capture_output=True)
    subprocess.run(
        [
            "openssl",
            "req",
            "-x509",
            "-new",
            "-key",
            str(key_path),
            "-out",
            str(cert_path),
            "-days",
            "365",
            "-subj",
            f"/CN={common_name}",
        ],
        check=True,
        capture_output=True,
    )
    return key_path, cert_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cert", help="path to an existing public certificate (.crt)")
    parser.add_argument("--app-id", default=client_id, help="application (client) ID to check")
    parser.add_argument("--name", default="office365-rest-python-client", help="certificate display name")
    parser.add_argument("--warn-days", type=int, default=DEFAULT_WARN_DAYS)
    args = parser.parse_args()

    client = _privileged_client()
    app = client.applications.get_by_app_id(args.app_id).get().execute_query()
    certs = app.key_credentials

    if certs:
        newest = max(certs, key=lambda k: k.days_until_expiry if k.days_until_expiry is not None else 1 << 30)
        days = newest.days_until_expiry
        if days is None or days > args.warn_days:
            print(f"Newest certificate expires in {days} days — nothing to do.")
            return
        print(f"Newest certificate expires in {days} days — renewing...")

    if args.cert:
        cert_path = Path(args.cert)
    else:
        _, cert_path = _generate_certificate(Path(tempfile.mkdtemp()), args.name)

    app.add_certificate(cert_path.read_bytes(), args.name).execute_query()
    print(f"Uploaded {cert_path} to {app.display_name}.")


if __name__ == "__main__":
    main()
