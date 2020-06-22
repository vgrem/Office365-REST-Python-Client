from office365.runtime.auth.clientCredential import ClientCredential
from office365.runtime.auth.userCredential import UserCredential
from office365.runtime.auth.providers.acs_token_provider import ACSTokenProvider
from office365.runtime.auth.base_authentication_context import BaseAuthenticationContext
from office365.runtime.auth.providers.oauth_token_provider import OAuthTokenProvider
from office365.runtime.auth.providers.saml_token_provider import SamlTokenProvider


class AuthenticationContext(BaseAuthenticationContext):

    def __init__(self, url, credentials=None):
        """
        Authentication context for SharePoint Online/OneDrive

        :param str url:  authority url
        :param ClientCredential or UserCredential credentials: credentials
        """
        super(AuthenticationContext, self).__init__()
        self.url = url
        self.credentials = credentials
        self.provider = None

    def set_token(self, token):
        """
        Sets access token

        :type token: TokenResponse
        """
        self.provider = OAuthTokenProvider(self.url)
        self.provider.token = token

    def acquire_token(self):
        if isinstance(self.credentials, ClientCredential):
            return self.acquire_token_for_app(self.credentials.clientId, self.credentials.clientSecret)
        elif isinstance(self.credentials, UserCredential):
            return self.acquire_token_for_user(self.credentials.userName, self.credentials.password)
        else:
            raise ValueError("Unknown credential type")

    def acquire_token_for_user(self, username, password):
        """Acquire token via user credentials

        :type password: str
        :type username: str
        """
        self.provider = SamlTokenProvider(self.url, username, password)
        if not self.provider.acquire_token():
            raise ValueError('Acquire token failed: {0}'.format(self.provider.error))
        return True

    def acquire_token_for_app(self, client_id, client_secret):
        """Acquire token via client credentials (SharePoint App Principal)"""
        self.provider = ACSTokenProvider(self.url, client_id, client_secret)
        if not self.provider.acquire_token():
            raise ValueError('Acquire token failed: {0}'.format(self.provider.error))
        return True

    def acquire_token_password_grant(self, client_id, username, password, resource, scope):
        """
        Acquire token via resource owner password credential (ROPC) grant

        :param str resource: A URI that identifies the resource for which the token is valid.
        :param str username: : The username of the user on behalf this application is authenticating.
        :param str password: The password of the user named in the username parameter.
        :param str client_id: str The OAuth client id of the calling application.
        :param list[str] scope:
        """
        self.provider = OAuthTokenProvider(self.url)
        return self.provider.acquire_token_password_type(resource=resource,
                                                         client_id=client_id,
                                                         user_credentials=UserCredential(username, password),
                                                         scope=scope)

    def authenticate_request(self, request_options):
        """Authenticate request

        :type request_options: RequestOptions"""
        if isinstance(self.provider, SamlTokenProvider):
            request_options.set_header('Cookie', self.provider.get_authentication_cookie())
        elif isinstance(self.provider, ACSTokenProvider) or isinstance(self.provider, OAuthTokenProvider):
            request_options.set_header('Authorization', self.provider.get_authorization_header())
        else:
            raise ValueError('Unknown authentication provider')

    @property
    def is_authenticated(self):
        return self.provider and self.provider.is_authenticated()

    def get_last_error(self):
        return self.provider.get_last_error()
