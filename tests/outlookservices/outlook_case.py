from unittest import TestCase

from settings import settings

from office365.outlookservices.outlook_client import OutlookClient


class OutlookClientTestCase(TestCase):
    """SharePoint specific test case base class"""

    @classmethod
    def setUpClass(cls):
        client_id = settings.get('client_credentials').get('client_id')
        username = settings.get('user_credentials').get('username')
        password = settings.get('user_credentials').get('password')
        cls.client = OutlookClient.from_tenant(settings.get('tenant'))\
            .with_user_credentials(client_id, username, password)
