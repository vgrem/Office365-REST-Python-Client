"""
Creates calculated site field
"""
from office365.sharepoint.client_context import ClientContext
from tests import create_unique_name, test_client_credentials, test_team_site_url

client = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
field_name = create_unique_name("CalcColumn")
formula = '=CONCATENATE(Author,":",Created)'
field = client.web.fields.add_calculated(field_name, formula).execute_query()

print("Field  {0} has been created".format(field.internal_name))
field.delete_object().execute_query()  # clean up
