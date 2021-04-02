import csv
import os
import tempfile

from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_client_credentials

"Demonstrates how to export a List data as csv"

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
# 1.retrieve list data
list_title = "Contacts_Large"
list_to_export = ctx.web.lists.get_by_title(list_title)
list_items = list_to_export.items.top(100).get().execute_query()
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
