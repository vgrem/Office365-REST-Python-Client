from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
ctx.web.assign_document_id("MEDIADEVDOC").execute_query()
print("Document IDs has been assigned")
