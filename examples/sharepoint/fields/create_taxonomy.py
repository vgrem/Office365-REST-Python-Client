"""
Demonstrates how to create a site field of type Taxonomy
"""
import sys

from office365.sharepoint.client_context import ClientContext
from tests import create_unique_name, test_client_credentials, test_team_site_url

client = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

term_set_id = "3b712032-95c4-4bb5-952d-f85ae9288f99"
# term_sets = client.taxonomy.term_store.get_term_sets_by_name("Countries").execute_query()
# if len(term_sets) == 0:
#    sys.exit("No term sets found")

field_name = create_unique_name(create_unique_name("Country"))
field = client.web.fields.create_taxonomy_field(field_name, term_set_id).execute_query()
print("Field  {0} has been created".format(field.internal_name))

field.delete_object().execute_query()  # clean up
