from settings import settings

from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.fileSystemObjectType import FileSystemObjectType


def print_progress(items_read):
    print("Items read: {0}".format(items_read))


def enum_items(target_list):
    items = target_list.items  # .top(1220)
    items.page_loaded += print_progress  # page load event
    ctx.load(items)
    ctx.execute_query()
    for index, item in enumerate(items):
        print("{0}: {1}".format(index, item.properties['Title']))


def enum_files_and_folders(target_list):
    """
    :type target_list: List
    """
    items = target_list.items.select(["FileSystemObjectType"]).expand(["File", "Folder"])
    ctx.load(items)
    ctx.execute_query()
    for item in items:
        if item.properties["FileSystemObjectType"] == FileSystemObjectType.Folder:
            print("Folder url: {0}".format(item.folder.serverRelativeUrl))
        else:
            print("File url: {0}".format(item.file.serverRelativeUrl))


def get_total_count(target_list):
    result = target_list.items.get_items_count()
    target_list.items.page_loaded += print_progress  # page load event
    ctx.execute_query()
    print("Total items count: {0}".format(result.value))


def get_items(target_list):
    items = target_list.items  # .top(1220)
    items.page_loaded += print_progress  # page load event
    ctx.load(items)
    ctx.execute_query()
    index = 1200
    print("Item at index: {0}".format(items[index].properties))


ctx = ClientContext.connect_with_credentials("https://mediadev8.sharepoint.com/sites/team",
                                             ClientCredential(settings['client_credentials']['client_id'],
                                                              settings['client_credentials']['client_secret']))

# list_source = ctx.web.lists.get_by_title("Contacts_Large")
list_source = ctx.web.lists.get_by_title("Documents_Archive")
enum_files_and_folders(list_source)
# get_total_count(list_source)
# get_items(list_source)
