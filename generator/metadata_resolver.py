from xml.dom import minidom

from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.sharepoint.client_context import ClientContext
from tests import test_site_url, test_client_credentials


def get_metadata(context):
    """
    :param office365.sharepoint.client_context.ClientContext context: SharePoint context
    """
    metadata_url = "/".join([context.service_root_url(), "$metadata"])
    request = RequestOptions(metadata_url)
    request.method = HttpMethod.Get
    response = context.pending_request().execute_request_direct(request)
    response.raise_for_status()
    return response.content


ctx = ClientContext(test_site_url).with_credentials(test_client_credentials)
metadata_path = "./metadata/SharePoint.xml"
metadata = get_metadata(ctx).decode("utf-8")
metadata_xml = minidom.parseString(metadata).toprettyxml(indent="   ")
with open(metadata_path, "w") as fh:
    fh.write(metadata_xml)
