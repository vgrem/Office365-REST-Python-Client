from unittest import TestCase

from client.auth.authentication_context import AuthenticationContext
from client.client_context import ClientContext
from examples.settings import settings


class SPTestCase(TestCase):
    """SharePoint specific test case base class"""

    @classmethod
    def setUpClass(cls):
        ctx_auth = AuthenticationContext(url=settings['url'])
        ctx_auth.acquire_token_for_user(username=settings['username'], password=settings['password'])
        cls.context = ClientContext(settings['url'], ctx_auth)



