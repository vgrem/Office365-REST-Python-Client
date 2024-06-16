"""
Demonstrates how to set taxonomy field value
"""

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.taxonomy.field_value import (
    TaxonomyFieldValue,
    TaxonomyFieldValueCollection,
)
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
custom_list = ctx.web.lists.get_by_title("Requests")


item = custom_list.add_item(
    {
        "Title": "New item",
        "Country": TaxonomyFieldValue("Sweden", "f9a6dae9-633c-474b-b35e-b235cf2b9e73"),
        "Countries": TaxonomyFieldValueCollection(
            [TaxonomyFieldValue("Sweden", "f9a6dae9-633c-474b-b35e-b235cf2b9e73")]
        ),
    }
).execute_query()
