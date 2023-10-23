from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.collection import ListItemCollection
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.lists.list import List
from tests import test_client_credentials, test_team_site_url


def print_progress(items):
    # type: (ListItemCollection) -> None
    print("Items read: {0}".format(len(items)))


def query_large_list(target_list):
    # type: (List) -> None
    paged_items = (
        target_list.items.paged(500, page_loaded=print_progress).get().execute_query()
    )
    for index, item in enumerate(paged_items):  # type: int, ListItem
        print("{0}: {1}".format(index, item.id))
    # all_items = [item for item in paged_items]
    # print("Total items count: {0}".format(len(all_items)))


def get_total_count(target_list):
    # type: (List) -> None
    all_items = target_list.items.get_all(5000, print_progress).execute_query()
    print("Total items count: {0}".format(len(all_items)))


def query_items_no_paged(target_list):
    # type: (List) -> None
    """
    Demonstrates the default behaviour where only
    """
    items = target_list.items.get().select(["Title"]).top(50).execute_query()
    print("Total items count: {0}".format(len(items)))


ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
large_list = ctx.web.lists.get_by_title("Contacts_Large")
# query_large_list(large_list)
get_total_count(large_list)
# query_items_no_paged(large_list)
