from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.taxonomy.field_value import TaxonomyFieldValueCollection, TaxonomyFieldValue
from tests import test_team_site_url, test_client_credentials, create_unique_name

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
custom_list = ctx.web.add_list(create_unique_name("Custom List")).execute_query()


print("Adding a taxonomy field into list '{0}'...".format(custom_list.title))
term_set_id = "3b712032-95c4-4bb5-952d-f85ae9288f99"
tax_field = custom_list.fields.create_taxonomy_field("Country", term_set_id).execute_query()
multi_tax_field = custom_list.fields.create_taxonomy_field("Countries", term_set_id,
                                                           allow_multiple_values=True).execute_query()

print("Creating list item...")
item = custom_list.add_item({
    "Title": "New item"
}).execute_query()

print("Updating list item...")
item.set_property("Country", TaxonomyFieldValue("Sweden", "f9a6dae9-633c-474b-b35e-b235cf2b9e73"))
item.set_property("Countries",
                  TaxonomyFieldValueCollection([TaxonomyFieldValue("Sweden", "f9a6dae9-633c-474b-b35e-b235cf2b9e73")]))
item.update().execute_query()

print("Cleaning up temporary resources...")
custom_list.delete_object().execute_query()
