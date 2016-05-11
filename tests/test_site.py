from unittest import TestCase
from client.auth.authentication_context import AuthenticationContext
from client.client_context import ClientContext
from examples.settings import settings


class TestSite(TestCase):
    def setUp(self):
        ctx_auth = AuthenticationContext(url=settings['url'])
        ctx_auth.acquire_token_for_user(username=settings['username'], password=settings['password'])
        self.context = ClientContext(settings['url'], ctx_auth)

    def test_if_site_loaded(self):
        site = self.context.site
        self.context.load(site)
        self.context.execute_query()
        self.assertIsNotNone(site.properties['Url'], "Site resource was not requested")
