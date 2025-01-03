"""
Gets Term by id
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
term_guid = "f9a6dae9-633c-474b-b35e-b235cf2b9e73"
taxonomy_list = ctx.web.lists.get_by_title("TaxonomyHiddenList")
result = (
    taxonomy_list.items.first("IdForTerm eq '{0}'".format(term_guid))
    .get()
    .execute_query()
)
print(result.properties.get("Title"))
