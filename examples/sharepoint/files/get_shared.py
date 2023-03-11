import os
import tempfile
from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_client_credentials

client = ClientContext(test_team_site_url).with_credentials(test_client_credentials)


sharing_link_url = "https://mediadev8.sharepoint.com/:x:/s/team/EcEbi_M2xQJLng_bvQjPtgoB1rB6BFvMVFixnf4wOxfE5w?e=bzNjb6"

download_path = os.path.join(tempfile.mkdtemp(), "Report.csv")
with open(download_path, "wb") as local_file:
    file = client.web.get_file_by_guest_url(sharing_link_url).download(local_file).execute_query()
print("[Ok] file has been downloaded into: {0}".format(download_path))


