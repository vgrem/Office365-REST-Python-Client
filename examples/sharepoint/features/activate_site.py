from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.features.definitions.scope import FeatureDefinitionScope
from office365.sharepoint.features.known_list import KnownFeaturesList
from tests import test_team_site_url, test_client_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
f = ctx.site.features.add(KnownFeaturesList.DocId, False, FeatureDefinitionScope.Farm).execute_query()
print("Feature {0} has been activated.", f.display_name)
