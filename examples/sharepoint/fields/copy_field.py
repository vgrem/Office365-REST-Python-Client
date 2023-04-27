from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_client_credentials, test_site_url


def clean_up(field_to_del):
    field_to_del.delete_object().execute_query()


source_site_url = test_team_site_url
target_site_url = test_site_url
field_name = "DocScope"

source_ctx = ClientContext(source_site_url).with_credentials(test_client_credentials)
source_field = source_ctx.web.default_document_library().fields.get_by_internal_name_or_title(field_name)
source_ctx.load(source_field, ["SchemaXml"]).execute_query()

target_ctx = ClientContext(target_site_url).with_credentials(test_client_credentials)
target_list = target_ctx.web.default_document_library()
target_field = target_list.fields.create_field_as_xml(source_field.schema_xml).execute_query()
clean_up(target_field)
