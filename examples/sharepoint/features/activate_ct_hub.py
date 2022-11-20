from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.features.definitions.scope import FeatureDefinitionScope
from tests import test_client_credentials, test_site_url

feature_id = "9a447926-5937-44cb-857a-d3829301c73b"

ctx = ClientContext(test_site_url).with_credentials(test_client_credentials)
f = ctx.site.features.add(feature_id, False, FeatureDefinitionScope.Farm).execute_query()
print("Feature {0} has been activated.", f.display_name)
