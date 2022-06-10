from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.taxonomy.field_value import TaxonomyFieldValue, TaxonomyFieldValueCollection
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

tasks_list = ctx.web.lists.get_by_title("Tasks")


tax_field_value = TaxonomyFieldValue("Sweden", "f9a6dae9-633c-474b-b35e-b235cf2b9e73")
item_to_create = tasks_list.add_item({
    "Title": "New task",
    "Country": tax_field_value,
    "Countries": TaxonomyFieldValueCollection([tax_field_value])
}).execute_query()
print("List item created.")
