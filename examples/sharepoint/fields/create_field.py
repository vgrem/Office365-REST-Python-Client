import uuid

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.fields.field_calculated import FieldCalculated
from office365.sharepoint.fields.field_creation_information import FieldCreationInformation
from office365.sharepoint.fields.field_type import FieldType
from tests import test_client_credentials, test_team_site_url

client = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

field_name = "AuthorInfo_" + uuid.uuid4().hex
create_field_info = FieldCreationInformation(field_name, FieldType.Calculated)
create_field_info.set_property("Formula", '=CONCATENATE(Author,":",Created)')
created_field = client.site.root_web.fields.add(create_field_info).execute_query()  # type: FieldCalculated
print(f"Calculated field with formula {created_field.formula} has been created")
