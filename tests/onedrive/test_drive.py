from tests.graph_case import GraphTestCase


class TestDrive(GraphTestCase):
    """OneDrive specific test case base class"""

    def test1_get_drives(self):
        drives = self.client.drives.top(2).get().execute_query()
        self.assertLessEqual(len(drives), 2)
        for drive in drives:
            self.assertIsNotNone(drive.web_url)

    def test2_get_drives_alt(self):
        resp = self.client.execute_request_direct("drives?$top=2")
        drives = resp.json()["value"]
        self.assertLessEqual(len(drives), 2)
        for drive in drives:
            self.assertIsNotNone(drive["webUrl"])

    def test3_get_first_drive(self):
        drives = self.client.drives.get().top(10).execute_query()
        self.assertGreaterEqual(len(drives), 1)
        target_drive_id = drives[0].id

        target_drive = self.client.drives[target_drive_id].get().execute_query()
        self.assertEqual(target_drive.id, target_drive_id)

    def test4_get_site(self):
        site = self.client.sites.root.get().execute_query()
        self.assertIsNotNone(site.resource_path)

    def test5_get_recent(self):
        items = self.client.me.drive.recent().execute_query()
        self.assertIsNotNone(items.resource_path)

    def test4_search_drive(self):
        items = self.client.me.drive.search("Guide.docx").execute_query()
        self.assertIsNotNone(items.resource_path)

    def test5_shared_with_me(self):
        col = self.client.me.drive.shared_with_me().execute_query()
        self.assertIsNotNone(col.resource_path)

    # def test6_list_bundles(self):
    #    result = self.client.me.drive.bundles.get().execute_query()
    #    self.assertIsNotNone(result.resource_path)

    def test7_list_changes(self):
        result = self.client.me.drive.root.delta.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    # def test8_get_delta_link(self):
    #    result = self.client.me.drive.root.delta.token("latest").get().execute_query()
    #    self.assertIsNotNone(result.resource_path)
