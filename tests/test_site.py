from client.runtime.resource_path_entry import ResourcePathEntry
from client.runtime.resource_path_service_operation import ResourcePathServiceOperation
from tests.sharepoint_case import SPTestCase


class TestSite(SPTestCase):
    def test_if_site_loaded(self):

        site_path = ResourcePathEntry(self.context, None, "Site")
        web_path = ResourcePathEntry(self.context, site_path, "RootWeb")
        lists_path = ResourcePathEntry(self.context, web_path, "Lists")
        list_path = ResourcePathServiceOperation(self.context, lists_path, "GetByTitle", ["Title"])
        url = list_path.build_path_url()

        site = self.context.site
        self.context.load(site)
        self.context.execute_query()
        self.assertIsNotNone(site.properties['Url'], "Site resource was not requested")
