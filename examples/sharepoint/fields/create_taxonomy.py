"""
Demonstrates how to create a site field of type Taxonomy
"""

from office365.sharepoint.client_context import ClientContext
from tests import create_unique_name, test_client_credentials, test_team_site_url

client = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

# term_sets = client.taxonomy.term_store.get_term_sets_by_name("Sweden").execute_query()

# field_name = create_unique_name("TaxColumn")
# field = client.web.fields.create_taxonomy_field(field_name).execute_query()
# print("Field  {0} has been created".format(field.internal_name))
# field.delete_object().execute_query()  # clean up
