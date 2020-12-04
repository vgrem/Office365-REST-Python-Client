from office365.runtime.auth.client_credential import ClientCredential
from office365.runtime.auth.providers.acs_token_provider import ACSTokenProvider
from office365.runtime.auth.providers.oauth_token_provider import OAuthTokenProvider
from office365.runtime.auth.providers.saml_token_provider import SamlTokenProvider
from office365.runtime.auth.user_credential import UserCredential


class AuthenticationContext(object):

    def __init__(self, url):
        """
        Authentication context for SharePoint Online/OneDrive

        :param str url:  authority url
        """
        self.url = url
        self._provider = None

    def register_provider(self, credentials_or_token_func):
        if callable(credentials_or_token_func):
            self._provider = OAuthTokenProvider(credentials_or_token_func)
        elif isinstance(credentials_or_token_func, ClientCredential):
            self._provider = ACSTokenProvider(self.url, credentials_or_token_func.clientId,
                                              credentials_or_token_func.clientSecret)
        elif isinstance(credentials_or_token_func, UserCredential):
            self._provider = SamlTokenProvider(self.url, credentials_or_token_func.userName,
                                               credentials_or_token_func.password)
        else:
            raise ValueError("Unknown credential type")

    def acquire_token_for_user(self, username, password):
        """Acquire token via user credentials
        Status: deprecated!

        :type password: str
        :type username: str
        """
        self._provider = SamlTokenProvider(url=self.url, username=username, password=password)
        return self._provider.ensure_authentication_cookie()

    def acquire_token_for_app(self, client_id, client_secret):
        """Acquire token via client credentials (SharePoint App Principal)
        Status: deprecated!
        """
        self._provider = ACSTokenProvider(url=self.url, client_id=client_id, client_secret=client_secret)
        return self._provider.ensure_app_only_access_token()

    def authenticate_request(self, request):
        """Authenticate request
        :type request: RequestOptions"""
        self._provider.authenticate_request(request)
