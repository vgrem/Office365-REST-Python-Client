import json
import os
from unittest import TestCase

from office365.graph_client import GraphClient
from settings import settings


def get_token(auth_ctx):
    client_id, client_secret = os.environ['Office365_Python_Sdk_ClientCredentials'].split(';')
    token = auth_ctx.acquire_token_with_client_credentials(
        "https://graph.microsoft.com",
        client_id,
        client_secret)
    return token


class TestDrive(TestCase):
    """OneDrive specific test case base class"""

    @classmethod
    def setUpClass(cls):
        ci_tenant_name = settings['tenant']
        cls.client = GraphClient(ci_tenant_name, get_token)

    def test1_get_drives(self):
        drives = self.client.drives.top(2)
        self.client.load(drives)
        self.client.execute_query()
        self.assertLessEqual(len(drives), 2)
        for drive in drives:
            self.assertIsNotNone(drive.web_url)

    def test2_get_drives_alt(self):
        resp = self.client.execute_request("/drives?$top=2")
        drives = json.loads(resp.content)['value']
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
