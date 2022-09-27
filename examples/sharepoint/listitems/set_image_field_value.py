import json
import os
import sys

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.listitem import ListItem
from tests import test_team_site_url, test_client_credentials


def upload_image(web, file_path):
    """
    :type web: office365.sharepoint.webs.web.Web
    :type file_path: str
    """
    with open(file_path, 'rb') as content_file:
        file_content = content_file.read()
    lib = web.lists.ensure_site_assets_library().execute_query()
    file = lib.root_folder.upload_file(os.path.basename(file_path), file_content).execute_query()
    return file.serverRelativeUrl


ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

image_url = upload_image(ctx.web, "../../data/Office_365_logo.png")
field_name = "Image"
lib_title = "HRDocs"

doc_lib = ctx.web.lists.get_by_title(lib_title)
items = doc_lib.items.get().top(1).execute_query()
if len(items) == 0:
    sys.exit("No items were found")

# 1. Retrieve image field and value
# image_field = doc_lib.fields.get_by_internal_name_or_title(field_name).get().execute_query()
# image_field_value = items[0].get_property(field_name)


# 2.Set image field value
first_item = items[0]  # type: ListItem
# field_value = ImageFieldValue(image_url)
field_value_raw = json.dumps({"serverRelativeUrl": image_url})
first_item.set_property(field_name, field_value_raw).update().execute_query()
print("Item has been updated")
