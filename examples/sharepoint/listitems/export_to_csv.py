"""
Demonstrates how to export a list items into csv file
"""

import csv
import os
import tempfile

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

# 1.retrieve list data
tasks_list = ctx.web.lists.get_by_title("Company Tasks")
items = tasks_list.items.top(100).get().execute_query()

# 2.export to a file
path = os.path.join(tempfile.mkdtemp(), "Contacts.csv")
with open(path, "w") as fh:
    fields = items[0].properties.keys()
    w = csv.DictWriter(fh, fields)
    w.writeheader()
    for item in items:
        w.writerow(item.properties)
print("List data has been exported into '{0}' file".format(path))
