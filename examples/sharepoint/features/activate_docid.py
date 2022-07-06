from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.features.definition_scope import FeatureDefinitionScope
from tests import test_team_site_url, test_client_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
feature_id = "b50e3104-6812-424f-a011-cc90e6327318"
f = ctx.site.features.add(feature_id, False, FeatureDefinitionScope.Farm).execute_query()
print("Feature {0} has been activated.", f.display_name)
