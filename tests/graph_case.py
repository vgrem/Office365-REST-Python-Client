from unittest import TestCase

import msal
from settings import settings

from office365.graph_client import GraphClient


def get_token():
    """
    Acquire token via MSAL ROPC flow!

    """
    authority_url = 'https://login.microsoftonline.com/{0}'.format(settings['tenant'])
    app = msal.PublicClientApplication(
        authority=authority_url,
        client_id=settings.get('client_credentials').get('client_id')
    )
    result = app.acquire_token_by_username_password(username=settings.get('user_credentials').get('username'),
                                                    password=settings.get('user_credentials').get('password'),
                                                    scopes=["https://graph.microsoft.com/.default"])
    return result


class GraphTestCase(TestCase):
    """Microsoft Graph specific test case base class"""
    client = None  # type: GraphClient

    @classmethod
    def setUpClass(cls):
        cls.client = GraphClient(get_token)
