"""
Demonstrates how to authenticate with user credentials (username and password) in non-interactive mode
"""
from examples import sample_site_url, sample_username, sample_password
from office365.sharepoint.client_context import ClientContext

ctx = ClientContext(sample_site_url).with_user_credentials(sample_username, sample_password)
web = ctx.web.get().execute_query()
print(web.url)
