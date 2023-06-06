"""
Delete a SharePoint list
"""
from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url


ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
list_to_del = ctx.web.lists.get_by_title("My list")
list_to_del.delete_object().execute_query()
