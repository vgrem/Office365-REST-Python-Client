from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.documentmanagement.document_set import DocumentSet
from tests import test_team_site_url, test_client_credentials

client = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
target_folder = client.web.default_document_library().root_folder.folders.get_by_url("2017")

doc_set = DocumentSet.create(client, target_folder, "07").execute_query()
print("DocSet created: {0}".format(doc_set.name))
