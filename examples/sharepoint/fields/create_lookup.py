"""
Demonstrates how to create lookup field
"""
from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_client_credentials, create_unique_name

field_name = create_unique_name("MultilookupField")
client = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
lookup_list = client.web.default_document_library()

lookup_field = client.web.fields.add_lookup_field(title=field_name,
                                                  lookup_list=lookup_list,
                                                  lookup_field_name='Title',
                                                  allow_multiple_values=True).execute_query()
print(f"Field  {lookup_field.internal_name} has been created")
lookup_field.delete_object().execute_query()
