from unittest import TestCase

from office365.runtime.auth.clientCredential import ClientCredential
from settings import settings
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext


class SPTestCase(TestCase):
    """SharePoint specific test case base class"""

    client = None
    client_id = settings.get('client_credentials').get('client_id')
    client_secret = settings.get('client_credentials').get('client_secret')
    site_url = settings.get('url')

    @classmethod
    def setUpClass(cls):
        ctx_auth = AuthenticationContext(url=cls.site_url)
        ctx_auth.acquire_token_for_app(client_id=cls.client_id,
                                       client_secret=cls.client_secret)
        cls.client = ClientContext(settings['url'], ctx_auth)

    @property
    def credentials(self):
        return ClientCredential(self.client_id, self.client_secret)
