from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.system_object_type import FileSystemObjectType
from office365.sharepoint.listitems.listitem import ListItem
from tests import test_team_site_url, test_client_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
doc_lib = ctx.web.lists.get_by_title("Documents_Archive")
items = doc_lib.items.select(["FileSystemObjectType"]).expand(["File", "Folder"]).get().execute_query()
for item in items:  # type: ListItem
    if item.file_system_object_type == FileSystemObjectType.Folder:
        print("(Folder): {0}".format(item.folder.serverRelativeUrl))
    else:
        print("(File): {0}".format(item.file.serverRelativeUrl))
