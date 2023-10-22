from office365.sharepoint.features.feature import Feature
from tests.sharepoint.sharepoint_case import SPTestCase


class TestFeature(SPTestCase):
    target_feature = None  # type: Feature

    def test_1_get_site_features(self):
        site_features = self.client.site.features.get().execute_query()
        self.assertGreater(len(site_features), 0)
