from unittest import TestCase
from settings import settings
from office365.outlookservices.outlook_client import OutlookClient
from office365.runtime.auth.authentication_context import AuthenticationContext


class OutlookClientTestCase(TestCase):
    """SharePoint specific test case base class"""

    @classmethod
    def setUpClass(cls):
        ctx_auth = AuthenticationContext(url=settings['tenant'])
        ctx_auth.acquire_token_password_grant(client_credentials=settings['client_credentials'],
                                              user_credentials=settings['user_credentials'])
        cls.client = OutlookClient(ctx_auth)
