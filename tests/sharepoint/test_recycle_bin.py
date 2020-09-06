from office365.sharepoint.recyclebin.recycleBinItemCollection import RecycleBinItemCollection
from tests.sharepoint.sharepoint_case import SPTestCase


class TestSharePointRecycleBin(SPTestCase):

    def test1_get_site_recycle_bin_items(self):
        items = self.client.site.get_recycle_bin_items().execute_query()
        self.assertIsInstance(items, RecycleBinItemCollection)
