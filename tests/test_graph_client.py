from office365.onedrive.internal.paths.resource_path_url import ResourcePathUrl
from office365.runtime.resource_path import ResourcePath
from tests.graph_case import GraphTestCase


class TestGraphClient(GraphTestCase):

    def test1_execute_batch_get_requests(self):
        current_user = self.client.me.get()  # 1.1: construct query to retrieve current user
        my_drive = self.client.me.drive.get()  # 1.2: construct query to retrieve my drive
        self.client.execute_batch()  # 2:submit query to the server
        self.assertIsNotNone(current_user.id)
        self.assertIsNotNone(my_drive.web_url)

    def test2_build_resource_path(self):
        path = ResourcePath("root", ResourcePath("drive", self.client.me.resource_path))
        self.assertEqual(path.to_url(), "/me/drive/root")

    def test3_build_url_resource_path(self):
        path = ResourcePathUrl("Sample.docx", ResourcePath("root", ResourcePath("drive", self.client.me.resource_path)))
        self.assertEqual(path.to_url(), "/me/drive/root:/Sample.docx:/")

    def test4_build_url_nested_resource_path(self):
        parent_path = ResourcePath("root", ResourcePath("drive", self.client.me.resource_path))
        path = ResourcePathUrl("Sample.docx", ResourcePathUrl("2018", ResourcePathUrl("archive", parent_path)))
        self.assertEqual(str(path), "/me/drive/root:/archive/2018/Sample.docx:/")
        self.assertEqual(path.name, "Sample.docx")

    def test5_build_operation_resource_path(self):
        path = self.client.me.drive.root.get_activities_by_interval().resource_path
        self.assertEqual(path.to_url(), "/me/drive/root/getActivitiesByInterval()")
