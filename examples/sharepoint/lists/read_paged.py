from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.collection import ListItemCollection
from office365.sharepoint.listitems.listitem import ListItem
from tests import test_client_credentials, test_team_site_url


def print_progress(items):
    # type: (ListItemCollection) -> None
    print("Items read: {0}".format(len(items)))


ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
large_list = ctx.web.lists.get_by_title("Contacts_Large")
paged_items = (
    large_list.items.paged(5000, page_loaded=print_progress).get().execute_query()
)
for index, item in enumerate(paged_items):  # type: int, ListItem
    pass
    # print("{0}: {1}".format(index, item.id))
