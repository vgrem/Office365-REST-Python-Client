import csv
import os
import tempfile

from settings import settings

from office365.runtime.auth.clientCredential import ClientCredential
from office365.sharepoint.client_context import ClientContext

"Demonstrates how to export a List data"

ctx = ClientContext.connect_with_credentials("https://mediadev8.sharepoint.com/sites/team",
                                             ClientCredential(settings['client_credentials']['client_id'],
                                                              settings['client_credentials']['client_secret']))
# 1.retrieve list data
list_title = "Contacts_Large"
list_to_export = ctx.web.lists.get_by_title(list_title)
list_items = list_to_export.items.top(100)
ctx.load(list_items)
ctx.execute_query()
if len(list_items) == 0:
    print("No data found")

# 2.export to a file
path = os.path.join(tempfile.mkdtemp(), "Contacts.csv")
with open(path, 'w') as fh:
    fields = list_items[0].properties.keys()
    w = csv.DictWriter(fh, fields)
    w.writeheader()
    for item in list_items:
        w.writerow(item.properties)
print("List data has been exported into '{0}' file".format(path))
