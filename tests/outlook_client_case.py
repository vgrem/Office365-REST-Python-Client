from unittest import TestCase
from examples.settings import settings
from office365.outlookservices.outlook_client import OutlookClient
from office365.runtime.auth.authentication_context import AuthenticationContext


class OutlookClientTestCase(TestCase):
    """SharePoint specific test case base class"""

    @classmethod
    def setUpClass(cls):
        # Due to Outlook REST API v1.0 BasicAuth Deprecation
        # (refer https://developer.microsoft.com/en-us/office/blogs/outlook-rest-api-v1-0-basicauth-deprecation/)
        # NetworkCredentialContext class should be no longer utilized
        # ctx_auth = NetworkCredentialContext(username=settings['user_credentials']['username'],
        #                                    password=settings['user_credentials']['password'])
        ctx_auth = AuthenticationContext(url=settings['tenant'])
        ctx_auth.acquire_token_password_grant(client_id=settings['client_credentials']['client_id'],
                                              client_secret=settings['client_credentials']['client_secret'],
                                              user_name=settings['user_credentials']['username'],
                                              password=settings['user_credentials']['password'])
        cls.client = OutlookClient(ctx_auth)
