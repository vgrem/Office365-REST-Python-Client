from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.pages.template_file_type import TemplateFileType
from tests import test_team_site_url, test_user_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)
parent_folder = ctx.web.default_document_library().root_folder

file_url = "WikiPage 123.aspx"
file = parent_folder.files.add_template_file(
    file_url, TemplateFileType.WikiPage
).execute_query()

file.delete_object().execute_query()
