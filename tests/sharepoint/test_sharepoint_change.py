from tests.sharepoint.sharepoint_case import SPTestCase

from office365.sharepoint.changes.changeCollection import ChangeCollection
from office365.sharepoint.changes.changeQuery import ChangeQuery


class TestChange(SPTestCase):

    def test_1_get_web_changes(self):
        changes = self.client.site.rootWeb.get_changes(query=ChangeQuery(web=True))
        self.client.execute_query()
        self.assertIsInstance(changes, ChangeCollection)

    def test_2_get_list_changes(self):
        target_list = self.client.site.rootWeb.default_document_library()
        self.client.load(target_list)
        self.client.execute_query()

        changes = target_list.get_changes(query=ChangeQuery(list_=True))
        self.client.execute_query()
        self.assertIsInstance(changes, ChangeCollection)
