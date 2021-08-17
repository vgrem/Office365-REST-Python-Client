from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

target_list = ctx.web.lists.get_by_title("Tasks")
target_field = target_list.fields.get_by_internal_name_or_title("AssignedTo")

#target_field.set_show_in_new_form(True)
#target_field.set_show_in_edit_form(True)
#target_field.set_show_in_display_form(True)
target_field.hidden = True
target_field.update().execute_query()



