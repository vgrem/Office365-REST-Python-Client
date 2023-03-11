from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.fields.field import Field
from tests import test_client_credentials, test_team_site_url

client = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

web_fields = client.web.fields.get().execute_query()
for f in web_fields:  # type: Field
    print(f"Field name {f.internal_name}")
