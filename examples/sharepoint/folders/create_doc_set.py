"""
Creates a new Document Set.

https://support.microsoft.com/en-us/office/introduction-to-document-sets-3dbcd93e-0bed-46b7-b1ba-b31de2bcd234

See https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/folder-operations
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, team_site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Creates a new Document Set")
    parser.add_argument("--name", default="Project", help="document set name")
    args = parser.parse_args()

    ctx = ClientContext(team_site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    lib = ctx.web.default_document_library()
    doc_set = lib.create_document_set(args.name).execute_query()
    print(f"DocSet created: {doc_set.name}")


if __name__ == "__main__":
    main()
