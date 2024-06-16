"""
Retrieves file check out status

https://support.microsoft.com/en-us/office/check-out-or-check-in-files-in-a-document-library-acce24cd-ab39-4fcf-9c4d-1ce3050dc602
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
file_url = "SitePages/Home.aspx"
file = ctx.web.get_file_by_server_relative_url(file_url).get().execute_query()

if file.check_out_type == 0:
    print("The file is checked out for editing on the server")
elif file.check_out_type == 1:
    print("The file is checked out for editing on the local computer.")
else:
    print("The file is not checked out.")
