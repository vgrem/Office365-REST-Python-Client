from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.documentmanagement.document_set import DocumentSet
from tests import test_client_credentials, test_team_site_url

client = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
lib = client.web.default_document_library()
doc_set = DocumentSet.create(client, lib.root_folder, "07").execute_query()
print("DocSet created: {0}".format(doc_set.name))
