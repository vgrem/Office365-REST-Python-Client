from tests.sharepoint_case import SPTestCase


class TestList(SPTestCase):
    def test_read_list(self):
        list_title = "Tasks"
        list_obj = self.context.web.lists.get_by_title(list_title)
        ctx = list_obj.context
        ctx.load(list_obj)
        ctx.execute_query()
        self.assertEqual(list_title, list_obj.properties['Title'])
