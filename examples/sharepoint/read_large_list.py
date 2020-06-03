from office365.runtime.auth.ClientCredential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from settings import settings


def print_progress(items_read):
    print("Items read: {0}".format(items_read))


ctx = ClientContext.connect_with_credentials("https://mediadev8.sharepoint.com/sites/team",
                                             ClientCredential(settings['client_credentials']['client_id'],
                                                              settings['client_credentials']['client_secret']))

list_source = ctx.web.lists.get_by_title("Contacts_Large")
items = list_source.items
items.page_loaded += print_progress  # page load event
items.page_size = 400  # specify custom page size (default is 100)
ctx.load(items)
ctx.execute_query()

#print("Items count: {0}".format(len(items)))
for item in items:
    print("{0}".format(item.properties['Title']))
