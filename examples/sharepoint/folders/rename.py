"""
Demonstrates how to rename a folder
"""
from office365.sharepoint.client_context import ClientContext
from tests import create_unique_name, test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

folder = ctx.web.default_document_library().root_folder.add(
    create_unique_name("Orders - (2007)")
)  # create temp folder

folder.rename("OUT - (Drafts 123)").execute_query()

folder.delete_object().execute_query()
