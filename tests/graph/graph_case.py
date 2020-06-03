from unittest import TestCase

from office365.graph.graph_client import GraphClient
from settings import settings


def get_token(auth_ctx):
    """
    Get token
    :type auth_ctx: adal.AuthenticationContext
    """
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
