import csv
import os
import tempfile

from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_client_credentials


def export_to_csv(path, list_items):
    """
    :param str path: export path
    :param office365.sharepoint.listitems.collection.ListItemCollection list_items: List items
    """
    with open(path, 'w') as fh:
        fields = list_items[0].properties.keys()
        w = csv.DictWriter(fh, fields)
        w.writeheader()
        for item in list_items:
            w.writerow(item.properties)


ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
list_title = "Documents"
view_title = "All Documents"
list_view = ctx.web.lists.get_by_title(list_title).views.get_by_title(view_title)
export_items = list_view.get_items().execute_query()
export_path = os.path.join(tempfile.mkdtemp(), "DocumentsMetadata.csv")
export_to_csv(export_path, export_items)
print("List view has been exported into '{0}' file".format(export_path))
