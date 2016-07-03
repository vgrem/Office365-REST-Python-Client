from client.runtime.resource_path_entity import ResourcePathEntity
from tests.sharepoint_case import SPTestCase


class TestSite(SPTestCase):
    def test_if_site_loaded(self):

        #site_path = ResourcePathEntity(self.context, None, "Site")
        #web_path = ResourcePathEntity(self.context, site_path, "RootWeb")
        #r = web_path.build_path_url()

        site = self.context.site
        self.context.load(site)
        self.context.execute_query()
        self.assertIsNotNone(site.properties['Url'], "Site resource was not requested")
