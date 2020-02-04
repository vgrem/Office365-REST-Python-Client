from unittest import TestCase

from office365.graphClient import GraphClient
from settings import settings

from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext


def get_token(auth_ctx):
    token = auth_ctx.acquire_token_with_username_password(
        'https://graph.microsoft.com',
        settings['user_credentials']['username'],
        settings['user_credentials']['password'],
        settings['client_credentials']['client_id'])
    return token


class GraphTestCase(TestCase):
    """Microsoft Graph specific test case base class"""
    client = None

    @classmethod
    def setUpClass(cls):
        cls.client = GraphClient(settings['tenant'], get_token)
