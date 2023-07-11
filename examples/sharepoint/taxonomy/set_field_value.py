"""
Demonstrates how to create a taxonomy field on a list and set taxonomy field value
"""

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.taxonomy.field_value import TaxonomyFieldValue, TaxonomyFieldValueCollection
from tests import test_client_credentials, test_team_site_url, create_unique_name

print("Creating a custom list...")
ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)


custom_list = ctx.web.add_list(create_unique_name("Custom List")).execute_query()

print("Adding a taxonomy field into list '{0}'...".format(custom_list.title))
term_set_id = "3b712032-95c4-4bb5-952d-f85ae9288f99"
tax_field = custom_list.fields.create_taxonomy_field("Country", term_set_id).execute_query()
multi_tax_field = custom_list.fields.create_taxonomy_field("Countries", term_set_id,
                                                           allow_multiple_values=True).execute_query()

print("Creating a list item and setting a taxonomy field value ...")
item = custom_list.add_item({
    "Title": "New item",
    "Country": TaxonomyFieldValue("Sweden", "f9a6dae9-633c-474b-b35e-b235cf2b9e73"),
    "Countries": TaxonomyFieldValueCollection([TaxonomyFieldValue("Sweden", "f9a6dae9-633c-474b-b35e-b235cf2b9e73")])
}).execute_query()

print("Cleaning up temporary resources...")
custom_list.delete_object().execute_query()
