import uuid

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.fields.calculated import FieldCalculated
from office365.sharepoint.fields.creation_information import FieldCreationInformation
from office365.sharepoint.fields.type import FieldType
from tests import test_client_credentials, test_team_site_url


def create_calculated_field(web):
    """
    :type web: office365.sharepoint.webs.web.Web
    """
    field_name = "CalculatedColumn" + uuid.uuid4().hex
    create_field_info = FieldCreationInformation(field_name, FieldType.Calculated)
    create_field_info.set_property("Formula", '=CONCATENATE(Author,":",Created)')
    return web.fields.add(create_field_info).execute_query()  # type: FieldCalculated


def create_date_field(web):
    field_name = "DateColumn" + uuid.uuid4().hex
    create_field_info = FieldCreationInformation(field_name, FieldType.DateTime)
    return web.fields.add(create_field_info).execute_query()


def clean_up(field_to_del):
    field_to_del.delete_object().execute_query()


client = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
# field = create_calculated_field(client.site.root_web)
field = create_date_field(client.site.root_web)
print(f"Field  {field.internal_name} has been created")
clean_up(field)
