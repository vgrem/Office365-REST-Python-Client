from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_client_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
component_id = "f0be2d8b-31af-4fb4-8ff2-3d5ebb1c103e"
ct_id = "0x01007D80E05D0D7D404F8EEDB79E0EF11AAA"

ct = ctx.web.content_types.get_by_id(ct_id)
ct.set_property("NewFormClientSideComponentId", component_id)
ct.update(True)
ctx.execute_query()
