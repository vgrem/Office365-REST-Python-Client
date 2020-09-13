from unittest import TestCase

import adal

from settings import settings

from office365.graph_client import GraphClient


def get_token():
    """
    Get token
    """
    authority_url = 'https://login.microsoftonline.com/{0}'.format(settings['tenant'])
    auth_ctx = adal.AuthenticationContext(authority_url)
    token = auth_ctx.acquire_token_with_username_password(
        'https://graph.microsoft.com',
        settings['user_credentials']['username'],
        settings['user_credentials']['password'],
        settings['client_credentials']['client_id'])
    return token


class GraphTestCase(TestCase):
    """Microsoft Graph specific test case base class"""
    client = None  # type: GraphClient

    @classmethod
    def setUpClass(cls):
        cls.client = GraphClient(get_token)
