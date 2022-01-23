from office365.runtime.auth.client_credential import ClientCredential
from office365.runtime.auth.providers.acs_token_provider import ACSTokenProvider
from office365.runtime.auth.providers.oauth_token_provider import OAuthTokenProvider
from office365.runtime.auth.providers.saml_token_provider import SamlTokenProvider
from office365.runtime.auth.token_response import TokenResponse
from office365.runtime.auth.user_credential import UserCredential


class AuthenticationContext(object):

    def __init__(self, authority_url):
        """
        Authentication context for SharePoint Online/OneDrive For Business

        :param str authority_url:  authority url
        """
        self.authority_url = authority_url
        self._provider = None

    def with_client_certificate(self, tenant, client_id, thumbprint, cert_path, **kwargs):
        """Creates authenticated SharePoint context via certificate credentials

        :param str tenant: Tenant name, for example {}@
        :param str cert_path: Path to A PEM encoded certificate private key.
        :param str thumbprint: Hex encoded thumbprint of the certificate.
        :param str client_id: The OAuth client id of the calling application.
        :param list[str] scopes (optional):  Scopes requested to access a protected API (a resource)
        """

        def _acquire_token_for_client_certificate():
            authority_url = 'https://login.microsoftonline.com/{0}'.format(tenant)
            credentials = {"thumbprint": thumbprint, "private_key": open(cert_path).read()}
            scopes = kwargs.get('scopes', ["{url}/.default".format(url=self.authority_url)])
            import msal
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
            self._provider = ACSTokenProvider(self.authority_url, credentials_or_token_func.clientId,
                                              credentials_or_token_func.clientSecret)
        elif isinstance(credentials_or_token_func, UserCredential):
            allow_ntlm = kwargs.get('allow_ntlm', False)
            if allow_ntlm:
                from office365.runtime.auth.providers.ntlm_provider import NtlmProvider
                self._provider = NtlmProvider(credentials_or_token_func.userName,
                                              credentials_or_token_func.password)
            else:
                browser_mode = kwargs.get('browser_mode', False)
                self._provider = SamlTokenProvider(self.authority_url, credentials_or_token_func.userName,
                                                   credentials_or_token_func.password, browser_mode)
        else:
            raise ValueError("Unknown credential type")

    def acquire_token_for_user(self, username, password, browser_mode=False):
        """Acquire token via user credentials
        Status: deprecated!

        :type password: str
        :type username: str
        :type browser_mode: str
        """
        self._provider = SamlTokenProvider(url=self.authority_url, username=username, password=password,
                                           browser_mode=browser_mode)
        return self._provider.ensure_authentication_cookie()

    def acquire_token_for_app(self, client_id, client_secret):
        """Acquire token via client credentials (SharePoint App Principal)
        Status: deprecated!
        """
        self._provider = ACSTokenProvider(url=self.authority_url, client_id=client_id, client_secret=client_secret)
        return self._provider.ensure_app_only_access_token()

    def authenticate_request(self, request):
        """
        Authenticate request
        :type request: office365.runtime.http.request_options.RequestOptions
        """
        self._provider.authenticate_request(request)
