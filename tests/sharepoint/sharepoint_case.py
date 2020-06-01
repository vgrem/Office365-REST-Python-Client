from unittest import TestCase
from settings import settings
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext


class SPTestCase(TestCase):
    """SharePoint specific test case base class"""

    client = None

    @classmethod
    def setUpClass(cls):
        ctx_auth = AuthenticationContext(url=settings['url'])
        # ctx_auth.acquire_token_for_user(username=settings['user_credentials']['username'],
        #                                password=settings['user_credentials']['password'])
        ctx_auth.acquire_token_for_app(client_id=settings['client_credentials']['client_id'],
                                       client_secret=settings['client_credentials']['client_secret'])
        cls.client = ClientContext(settings['url'], ctx_auth)
