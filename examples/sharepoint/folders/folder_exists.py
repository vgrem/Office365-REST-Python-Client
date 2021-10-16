from office365.runtime.client_request_exception import ClientRequestException
from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

# How to determine whether folder exist?

# Approach 1: explicitly specify Exists property
folder_rel_url = "/sites/team/Shared Documents/2022"
folder = ctx.web.get_folder_by_server_relative_url(folder_rel_url).select("Exists").get().execute_query()
if folder.exists:
    print("Folder is found")
else:
    print("Folder not found")


def try_get_folder(url):
    try:
        return ctx.web.get_folder_by_server_relative_url(url).get().execute_query()
    except ClientRequestException as e:
        if e.response.status_code == 404:
            return None
        else:
            raise ValueError(e.response.text)


# Approach 2
folder = try_get_folder(folder_rel_url)
if folder is None:
    print("Folder not found")




