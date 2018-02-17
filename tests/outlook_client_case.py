from unittest import TestCase
from examples.settings import settings
from office365.outlookservices.outlook_client import OutlookClient
from office365.runtime.auth.network_credential_context import NetworkCredentialContext


class OutlookClientTestCase(TestCase):
    """SharePoint specific test case base class"""

    @classmethod
    def setUpClass(cls):
        ctx_auth = NetworkCredentialContext(username=settings['user_credentials']['username'],
                                            password=settings['user_credentials']['password'])
        cls.client = OutlookClient(ctx_auth)
