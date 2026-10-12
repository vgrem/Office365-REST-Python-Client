"""
Add a new certificate to an app (rotate its key credential).

Uploads the *public* certificate (``.crt``); the private key stays local and is
what the client authenticates with. By default a self-signed pair is generated
with openssl into a temporary directory; pass ``--cert`` to upload an existing
certificate instead.

Usage:

    python rotate_cert.py                          # generate and upload
    python rotate_cert.py --cert /path/to/cert.crt # upload an existing certificate

Requires an interactive sign-in by a Global Administrator or Privileged Role
Administrator (the delegated ``Application.ReadWrite.All`` scope is carried by
the signed-in account).

Reference:
    https://learn.microsoft.com/en-us/graph/api/application-addcertificate
    https://learn.microsoft.com/en-us/entra/identity-platform/how-to-add-credentials
"""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path

from office365.graph_client import GraphClient
from tests.settings import admin_username, client_id, tenant


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
    parser.add_argument("--app-id", default=client_id, help="application (client) ID to rotate")
    parser.add_argument("--name", default="office365-rest-python-client", help="certificate display name")
    args = parser.parse_args()

    if args.cert:
        cert_path = Path(args.cert)
        key_path = cert_path.with_suffix(".pem")
    else:
        key_path, cert_path = _generate_certificate(Path(tempfile.mkdtemp()), args.name)

    client = _privileged_client()
    app = client.applications.get_by_app_id(args.app_id).get().execute_query()
    app.add_certificate(cert_path.read_bytes(), args.name).execute_query()
    print(f"Uploaded {cert_path} to {app.display_name}.")
    print(f"Keep the private key at: {key_path}")


if __name__ == "__main__":
    main()
