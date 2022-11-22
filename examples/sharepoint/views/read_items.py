from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.listitem import ListItem
from tests import test_client_credentials, test_team_site_url


def retrieve_default_view_items(context):
    """
    :type context: ClientContext
    """
    lib = context.web.default_document_library()
    items = lib.default_view.get_items().execute_query()
    for item in items:  # type: ListItem
        print(item.id)


def retrieve_custom_view_items(context):
    """
    :type context: ClientContext
    """
    view = context.web.lists.get_by_title("Contacts_Large").views.get_by_title("All contacts")
    items = view.get_items().top(5).execute_query()
    for item in items:  # type: ListItem
        print(item.id)


ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
retrieve_default_view_items(ctx)
#retrieve_custom_view_items(ctx)
