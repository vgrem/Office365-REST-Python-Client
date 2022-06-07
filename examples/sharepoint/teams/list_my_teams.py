from office365.runtime.client_request_exception import ClientRequestException
from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_user_credentials

try:
    ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)
    result = ctx.group_site_manager.get_current_user_joined_teams().execute_query()
except ClientRequestException as e:
    if e.message.startswith("AADSTS50173"):
        print(e.message)
    else:
        print(e.message)
