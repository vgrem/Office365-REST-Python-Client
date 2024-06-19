"""
This example deletes all the list items in a list.
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url


def print_progress(items_count):
    # type: (int) -> None
    print("List items count: {0}".format(target_list.item_count))


ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
target_list = ctx.web.lists.get_by_title("Company Tasks")
target_list.clear().get().execute_batch()
print("List items count: {0}".format(target_list.item_count))
