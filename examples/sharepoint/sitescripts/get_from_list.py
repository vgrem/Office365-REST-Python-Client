from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
target_list = ctx.web.default_document_library()
# This example creates the site script output from an existing list
result = target_list.get_site_script().execute_query()
print(result.value)
