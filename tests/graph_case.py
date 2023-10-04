from unittest import TestCase

import msal

from office365.graph_client import GraphClient
from tests import load_settings


def acquire_token_by_username_password():
    settings = load_settings()
    authority_url = "https://login.microsoftonline.com/{0}".format(
        settings.get("default", "tenant")
    )
    app = msal.PublicClientApplication(
        authority=authority_url,
        client_id=settings.get("client_credentials", "client_id"),
    )

    result = app.acquire_token_by_username_password(
        username=settings.get("user_credentials", "username"),
        password=settings.get("user_credentials", "password"),
        scopes=["https://graph.microsoft.com/.default"],
    )
    return result


def acquire_token_by_client_credentials():
    settings = load_settings()
    authority_url = "https://login.microsoftonline.com/{0}".format(
        settings.get("default", "tenant")
    )
    app = msal.ConfidentialClientApplication(
        authority=authority_url,
        client_id=settings.get("client_credentials", "client_id"),
        client_credential=settings.get("client_credentials", "client_secret"),
    )
    return app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])


class GraphTestCase(TestCase):
    """Microsoft Graph specific test case base class"""

    client = None  # type: GraphClient

    @classmethod
    def setUpClass(cls):
        cls.client = GraphClient(acquire_token_by_username_password)
