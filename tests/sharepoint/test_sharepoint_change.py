from office365.sharepoint.changes.changeCollection import ChangeCollection
from office365.sharepoint.changes.changeQuery import ChangeQuery
from tests.sharepoint.sharepoint_case import SPTestCase


class TestChange(SPTestCase):

    def test_1_list_web_changes(self):
        changes = self.client.site.rootWeb.get_changes(query=ChangeQuery())
        self.client.execute_query()
        self.assertIsInstance(changes, ChangeCollection)


