from office365.runtime.auth.ClientCredential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from settings import settings

ctx = ClientContext.connect_with_credentials("https://mediadev8.sharepoint.com/sites/team",
                                             ClientCredential(settings['client_credentials']['client_id'],
                                                              settings['client_credentials']['client_secret']))

large_list = ctx.web.lists.get_by_title("Contacts_Large")
paged_items = large_list.get_items().top(100)
ctx.load(paged_items)
ctx.execute_query()

#res = paged_items[102]
print("Items count: {0}".format(len(paged_items)))
#for idx, item in enumerate(paged_items):
#    print("{0}: {1}".format(idx, item.properties['Title']))
