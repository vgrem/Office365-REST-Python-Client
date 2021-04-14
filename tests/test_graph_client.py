from tests.graph_case import GraphTestCase


class TestGraphClient(GraphTestCase):

    def test1_execute_batch_get_requests(self):
        current_user = self.client.me.get()  # 1.1: construct query to retrieve current user
        my_drive = self.client.me.drive.get()  # 1.2: construct query to retrieve my drive
        self.client.execute_batch()  # 2:submit query to the server
        self.assertIsNotNone(current_user.id)
        self.assertIsNotNone(my_drive.web_url)
