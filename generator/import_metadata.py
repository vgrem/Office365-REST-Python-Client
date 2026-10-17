from argparse import ArgumentParser
from xml.dom import minidom

from office365.graph_client import GraphClient
from office365.sharepoint.client_context import ClientContext
from tests.settings import client_id, client_secret, password, site_url, tenant, username


def export_to_file(path: str, content: bytes) -> None:
    metadata_xml = minidom.parseString(content.decode("utf-8")).toprettyxml(indent="   ")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(metadata_xml)


parser = ArgumentParser()
parser.add_argument(
    "-e",
    "--endpoint",
    dest="endpoint",
    help="Import metadata endpoint",
    default="sharepoint",
)
parser.add_argument(
    "-p",
    "--path",
    dest="path",
    default="./metadata/SharePoint.xml",
    help="Import metadata endpoint",
)

args = parser.parse_args()

if args.endpoint == "sharepoint":
    print("Importing SharePoint model metadata...")
    ctx = ClientContext(site_url).with_username_and_password(tenant, client_id, username, password)
    result = ctx.get_metadata().execute_query()
    export_to_file(args.path, result.value)
elif args.endpoint == "graph":
    print("Importing Microsoft Graph model metadata...")
    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    result = client.get_metadata().execute_query()
    export_to_file(args.path, result.value)
