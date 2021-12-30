from xml.dom import minidom
from argparse import ArgumentParser

from examples import acquire_token_by_client_credentials
from office365.graph_client import GraphClient
from office365.sharepoint.client_context import ClientContext
from tests import test_site_url, test_client_credentials

parser = ArgumentParser()
parser.add_argument("-e", "--endpoint", dest="endpoint",
                    help="Import metadata endpoint", default="sharepoint")
parser.add_argument("-p", "--path",
                    dest="path", default="./metadata/SharePoint.xml",
                    help="Import metadata endpoint")

args = parser.parse_args()

if args.endpoint == "sharepoint":
    print("Importing SharePoint model metadata...")
    ctx = ClientContext(test_site_url).with_credentials(test_client_credentials)
    result = ctx.get_metadata().execute_query()
    metadata_xml = minidom.parseString(result.value.decode("utf-8")).toprettyxml(indent="   ")
    with open(args.path, "w") as fh:
        fh.write(metadata_xml)
elif args.endpoint == "microsoftgraph":
    print("Importing Microsoft Graph model metadata...")
    client = GraphClient(acquire_token_by_client_credentials)
    result = client.get_metadata().execute_query()
    metadata_xml = minidom.parseString(result.value.decode("utf-8")).toprettyxml(indent="   ")
    with open(args.path, "w") as fh:
        fh.write(metadata_xml)
