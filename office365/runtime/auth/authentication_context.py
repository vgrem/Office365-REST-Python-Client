import msal

from office365.runtime.auth.client_credential import ClientCredential
from office365.runtime.auth.providers.acs_token_provider import ACSTokenProvider
from office365.runtime.auth.providers.ntlm_provider import NtlmProvider
from office365.runtime.auth.providers.oauth_token_provider import OAuthTokenProvider
from office365.runtime.auth.providers.saml_token_provider import SamlTokenProvider
from office365.runtime.auth.token_response import TokenResponse
from office365.runtime.auth.user_credential import UserCredential


class AuthenticationContext(object):

    def __init__(self, url):
        """
        Authentication context for SharePoint Online/OneDrive

        :param str url:  authority url
        """
        self.url = url
        self._provider = None

    def with_client_certificate(self, tenant, client_id, thumbprint, cert_path):
        """Creates authenticated SharePoint context via certificate credentials

        :param str tenant: Tenant name, for example {}@
        :param str cert_path: Path to A PEM encoded certificate private key.
        :param str thumbprint: Hex encoded thumbprint of the certificate.
        :param str client_id: The OAuth client id of the calling application.
        """

        def _acquire_token_for_client_certificate():
            authority_url = 'https://login.microsoftonline.com/{0}'.format(tenant)
            scopes = [f"{self.url}/.default"]
            credentials = {"thumbprint": thumbprint, "private_key": open(cert_path).read()}
            app = msal.ConfidentialClientApplication(
                client_id,
                authority=authority_url,
                client_credential=credentials,
            )
            result = app.acquire_token_for_client(scopes)
            return TokenResponse.from_json(result)

        self.register_provider(_acquire_token_for_client_certificate)
        return self

    def register_provider(self, credentials_or_token_func, **kwargs):
        if callable(credentials_or_token_func):
            self._provider = OAuthTokenProvider(credentials_or_token_func)
        elif isinstance(credentials_or_token_func, ClientCredential):
            self._provider = ACSTokenProvider(self.url, credentials_or_token_func.clientId,
                                              credentials_or_token_func.clientSecret)
        elif isinstance(credentials_or_token_func, UserCredential):
            allow_ntlm = kwargs.get('allow_ntlm', False)
            if allow_ntlm:
                self._provider = NtlmProvider(credentials_or_token_func.userName,
                                              credentials_or_token_func.password)
            else:
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
