"""
Demonstrates how to create a taxonomy field on a list
"""

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.taxonomy.field_value import (
    TaxonomyFieldValue,
    TaxonomyFieldValueCollection,
)
from tests import create_unique_name, test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
custom_list = ctx.web.lists.get_by_title("Requests").get().execute_query()

term_set_id = "3b712032-95c4-4bb5-952d-f85ae9288f99"
tax_field_name = "Country"  # create_unique_name("Country")

print("1. Adding a taxonomy field into list '{0}'...".format(custom_list.title))
tax_field = custom_list.fields.create_taxonomy_field(
    tax_field_name, term_set_id
).execute_query()


print("2. Adding a taxonomy field into list '{0}'...".format(custom_list.title))
mult_tax_field_name = "Countries"  # create_unique_name("Countries")
multi_tax_field = custom_list.fields.create_taxonomy_field(
    mult_tax_field_name, term_set_id, allow_multiple_values=True
).execute_query()


# print("3. Deleting tax fields ...")
# tax_field.delete_object().execute_query()
# multi_tax_field.delete_object().execute_query()
