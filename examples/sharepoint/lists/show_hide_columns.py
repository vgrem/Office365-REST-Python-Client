from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url


def hide_column(t_list, field_name):
    """
    :type t_list: office365.sharepoint.lists.list.List
    :type field_name: str
    """
    field = t_list.fields.get_by_internal_name_or_title(field_name)
    # field.set_show_in_new_form(True)
    # field.set_show_in_edit_form(True)
    # field.set_show_in_display_form(True)
    field.hidden = True
    field.update().execute_query()


def show_column(t_list, field_name):
    """
    :type t_list: office365.sharepoint.lists.list.List
    :type field_name: str
    """
    field = t_list.fields.get_by_internal_name_or_title(field_name)
    field.hidden = False
    field.update().execute_query()


def add_column_to_view(view, field_name):
    """
    :type view: office365.sharepoint.views.view.View
    :type field_name: str
    """
    view.view_fields.add_view_field(field_name).execute_query()


def remove_column_from_view(view, field_name):
    """
    :type view: office365.sharepoint.views.view.View
    :type field_name: str
    """
    view.view_fields.remove_view_field(field_name).execute_query()


ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
target_list = ctx.web.lists.get_by_title("Tasks")
add_column_to_view(target_list.default_view, "AssignedTo")
# remove_column_from_view(target_list.default_view, "AssignedTo")
