from xml.dom import minidom

from office365.sharepoint.client_context import ClientContext
from tests import test_site_url, test_client_credentials


ctx = ClientContext(test_site_url).with_credentials(test_client_credentials)
metadata_path = "./metadata/SharePoint.xml"
result = ctx.get_metadata().execute_query()
metadata_xml = minidom.parseString(result.value.decode("utf-8")).toprettyxml(indent="   ")
with open(metadata_path, "w") as fh:
    fh.write(metadata_xml)
