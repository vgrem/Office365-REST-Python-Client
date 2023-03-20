"""
Example: SharePoint App-Only auth flow
https://learn.microsoft.com/en-us/sharepoint/dev/solution-guidance/security-apponly-azureacs
"""
from examples import sample_site_url, sample_client_id, sample_client_secret
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext

ctx = ClientContext(sample_site_url).with_credentials(ClientCredential(sample_client_id, sample_client_secret))
target_web = ctx.web.get().execute_query()
print(target_web.url)
