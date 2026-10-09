"""Upload a file, share it, and inspect the resulting link.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/sharing-rest-api
"""

import argparse
import json
import sys
from pathlib import Path

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.sharing.links.kind import SharingLinkKind
from office365.sharepoint.webs.web import Web
from tests.settings import cert_path, cert_thumbprint, client_id, team_site_url, tenant

SHARING_KIND_LABELS = {
    0: "Not initialized",
    1: "Direct/canonical link",
    2: "Organization view link",
    3: "Organization edit link",
    4: "Anonymous view link",
    5: "Anonymous edit link",
    6: "Tokenized link",
}


def main():
    parser = argparse.ArgumentParser(description="Upload a file, share it, and inspect the link")
    parser.add_argument(
        "--file",
        default=str(Path(__file__).resolve().parents[2] / "data" / "SharePoint User Guide.docx"),
        help="local file to upload",
    )
    args = parser.parse_args()

    ctx = ClientContext(team_site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    lib = ctx.web.default_document_library()
    with open(args.file, "rb") as f:
        remote_file = lib.root_folder.files.upload(f).execute_query()
    print(f"Uploaded: {remote_file.server_relative_url}")

    print("Creating an anonymous view link...")
    result = remote_file.share_link(SharingLinkKind.AnonymousView).execute_query()
    link_url = result.value.sharingLinkInfo.Url
    if link_url is None:
        sys.exit("Failed to create a sharing link")
    print(f"Link: {link_url}")

    result = Web.get_sharing_link_kind(ctx, link_url).execute_query()
    print(f"Kind: {SHARING_KIND_LABELS.get(result.value, 'Unknown')}")

    result = ctx.web.get_sharing_link_data(link_url).execute_query()
    print(json.dumps(result.value.to_json(), indent=4))

    remote_file.unshare_link(SharingLinkKind.AnonymousView).execute_query()
    print("Removed the anonymous view link")


if __name__ == "__main__":
    main()
