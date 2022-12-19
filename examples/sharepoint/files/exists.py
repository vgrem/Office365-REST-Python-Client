from office365.runtime.client_request_exception import ClientRequestException
from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_client_credentials


def try_get_file(web, url):
    """
    :type web: office365.sharepoint.webs.web.Web
    :type url: str
    """
    try:
        return web.get_file_by_server_relative_url(url).get().execute_query()
    except ClientRequestException as e:
        if e.response.status_code == 404:
            return None
        else:
            raise ValueError(e.response.text)


ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
file_url = '/sites/team/Shared Documents/big_buck_bunny111.mp4'
file = try_get_file(ctx.web, file_url)
if file is None:
    print("File not found")
