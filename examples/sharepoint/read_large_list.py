from office365.runtime.auth.ClientCredential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from settings import settings

ctx = ClientContext.connect_with_credentials("https://mediadev8.sharepoint.com/sites/team",
                                             ClientCredential(settings['client_credentials']['client_id'],
                                                              settings['client_credentials']['client_secret']))

large_list = ctx.web.lists.get_by_title("Contacts_Large")
items = large_list.items #.top(1000)
ctx.load(items)
ctx.execute_query()

print("Items count: {0}".format(len(items)))
for idx, item in enumerate(items):
    print("{0}: {1}".format(idx, item.properties['Title']))
