from unittest import TestCase
from office365.runtime.auth.clientCredential import ClientCredential
from office365.runtime.auth.userCredential import UserCredential
from office365.runtime.auth.providers.acs_token_provider import ACSTokenProvider
from office365.runtime.auth.providers.saml_token_provider import SamlTokenProvider
from office365.runtime.auth.tokenResponse import TokenResponse
from office365.sharepoint.client_context import ClientContext
from settings import settings

user_credentials = UserCredential(settings.get('user_credentials').get('username'),
                                  settings.get('user_credentials').get('password'))


class TestSharePointClient(TestCase):

    def test1_connect_with_app_principal(self):
        credentials = ClientCredential(settings.get('client_credentials').get('client_id'),
                                       settings.get('client_credentials').get('client_secret'))
        ctx = ClientContext.connect_with_credentials(settings['url'], credentials)
        self.assertIsInstance(ctx.authentication_context.provider, ACSTokenProvider)
        self.assertIsInstance(ctx.authentication_context.provider.token, TokenResponse)
        self.assertTrue(ctx.authentication_context.provider.token.is_valid)

    def test2_connect_with_user_credentials(self):
        ctx = ClientContext.connect_with_credentials(settings['url'], user_credentials)
        self.assertIsInstance(ctx.authentication_context.provider, SamlTokenProvider)

    def test3_init_from_url(self):
        ctx = ClientContext.from_url(settings['url']).with_credentials(user_credentials)
        web = ctx.web.load().execute_query()
        self.assertIsNotNone(web.url)

    def test2_connect_with_client_cert(self):
        pass
