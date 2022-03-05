import json

from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_client_credentials
list_title = "Site Pages"
view_title = "By Author"

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
list_object = ctx.web.lists.get_by_title(list_title)
# 1. First request to retrieve view fields
view_fields = list_object.views.get_by_title(view_title).view_fields.get().execute_query()
# 2. Second request to retrieve fields
fields = [list_object.fields.get_by_internal_name_or_title(field_name).get() for field_name in view_fields]
ctx.execute_batch()   # From performance perspective i would prefer execute_batch over execute_query here

fields_json = {f.internal_name: f.title for f in fields}
print(json.dumps(fields_json))
