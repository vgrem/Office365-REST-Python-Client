from office365.runtime.auth.ClientCredential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from settings import settings

ctx = ClientContext.connect_with_credentials("https://mediadev8.sharepoint.com/sites/team",
                                             ClientCredential(settings['client_credentials']['client_id'],
                                                              settings['client_credentials']['client_secret']))


def get_all_list_items():
    # 1st approach: get all list items
    list_source = ctx.web.lists.get_by_title("Contacts_Large")
    items = list_source.items
    ctx.load(items)
    ctx.execute_query()
    return items


def get_list_items_paged():
    list_source = ctx.web.lists.get_by_title("Contacts_Large")
    items = list_source.get_items()
    ctx.load(items)
    ctx.execute_query()
    return items


all_items = get_list_items_paged()
print("Items count: {0}".format(len(all_items)))
for idx, item in enumerate(all_items):
    print("{0}: {1}".format(idx, item.properties['Title']))
