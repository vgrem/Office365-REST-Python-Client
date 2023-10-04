from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

ct = ctx.web.content_types.get_by_name("Contoso Document")
ct.delete_object().execute_query()
