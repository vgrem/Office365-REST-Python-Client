from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

doc_lib = ctx.web.default_document_library()  # <- default_document_library refers to default Documents library
result = doc_lib.get_user_effective_permissions(ctx.web.current_user).execute_query()
print(result.value.permission_levels)
