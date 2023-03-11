from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_client_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
result = ctx.web.default_document_library().create_document_with_default_name("","docx").execute_query()
print(f"'{result.value}' file has been created")
