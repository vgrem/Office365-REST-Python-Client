from unittest import TestCase
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from examples.settings import settings


class SPTestCase(TestCase):
    """SharePoint specific test case base class"""

    @classmethod
    def setUpClass(cls):
        ctx_auth = AuthenticationContext(url=settings['url'])
        ctx_auth.acquire_token_for_user(username=settings['user_credentials']['username'],
                                        password=settings['user_credentials']['password'])
        cls.context = ClientContext(settings['url'], ctx_auth)

