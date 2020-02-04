from tests.graph_case import GraphTestCase


class TestDrive(GraphTestCase):
    """OneDrive specific test case base class"""
    target_file = None

    def test1_get_drives(self):
        drives = self.client.drives.top(2)
        self.client.load(drives)
        self.client.execute_query()
        self.assertLessEqual(len(drives), 2)
        for drive in drives:
            self.assertIsNotNone(drive.webUrl)

    def test2_get_drives_alt(self):
        resp = self.client.execute_request("/drives?$top=2")
        drives = resp.json()['value']
        self.assertLessEqual(len(drives), 2)
        for drive in drives:
            self.assertIsNotNone(drive['webUrl'])

    def test3_get_first_drive(self):
        drives = self.client.drives.top(1)
        self.client.load(drives)
        self.client.execute_query()
        self.assertLessEqual(len(drives), 1)
        target_drive_id = drives[0].id

        target_drive = self.client.drives.get_by_id(target_drive_id)
        self.client.load(target_drive)
        self.client.execute_query()
        self.assertEqual(target_drive.id, target_drive_id)
