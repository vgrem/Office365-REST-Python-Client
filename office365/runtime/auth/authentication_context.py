from office365.runtime.auth.authentication_provider import AuthenticationProvider
from office365.runtime.auth.client_credential import ClientCredential
from office365.runtime.auth.providers.acs_token_provider import ACSTokenProvider
from office365.runtime.auth.providers.saml_token_provider import SamlTokenProvider
from office365.runtime.auth.token_response import TokenResponse
from office365.runtime.auth.user_credential import UserCredential
from office365.runtime.compat import get_absolute_url


def _get_authorization_header(token):
    return '{token_type} {access_token}'.format(token_type=token.tokenType, access_token=token.accessToken)


class AuthenticationContext(object):
    """Authentication context for SharePoint Online/OneDrive For Business"""

    def __init__(self, url):
        """
        :param str url: SharePoint absolute web or site Url
        """
        self.url = url.rstrip("/")
        self._token_provider = None
        self._cached_token = None

    def with_client_certificate(self, tenant, client_id, thumbprint, cert_path=None, private_key=None, scopes=None):
        """Initializes a client to acquire a token via certificate credentials

        :param str tenant: Tenant name, for example {}@
        :param str client_id: The OAuth client id of the calling application.
        :param str thumbprint: Hex encoded thumbprint of the certificate.
        :param str or None cert_path: Path to A PEM encoded certificate private key.
        :param str or None private_key: A PEM encoded certificate private key.
        :param list[str] or None scopes:  Scopes requested to access a protected API (a resource)
        """
        if scopes is None:
            resource = get_absolute_url(self.url)
            scopes = ["{url}/.default".format(url=resource)]
        if cert_path is None and private_key is None:
            raise ValueError("Private key is missing. Use either 'cert_path' or 'private_key' to pass the value")
        elif cert_path is not None:
            with open(cert_path, 'r') as f:
                private_key = f.read()

        def _acquire_token_for_client_certificate():
            authority_url = 'https://login.microsoftonline.com/{0}'.format(tenant)
            credentials = {"thumbprint": thumbprint, "private_key": private_key}
            import msal
            app = msal.ConfidentialClientApplication(
                client_id,
                authority=authority_url,
                client_credential=credentials,
            )
            result = app.acquire_token_for_client(scopes)
            return TokenResponse.from_json(result)

        self.with_access_token(_acquire_token_for_client_certificate)
        return self

    def with_access_token(self, token_func):
        self._token_provider = token_func

    def with_credentials(self, credentials, **kwargs):
        """
        :param credentials:
        """
        if isinstance(credentials, ClientCredential):
            self._token_provider = ACSTokenProvider(self.url, credentials.clientId, credentials.clientSecret)
        elif isinstance(credentials, UserCredential):
            allow_ntlm = kwargs.get('allow_ntlm', False)
            if allow_ntlm:
                from office365.runtime.auth.providers.ntlm_provider import NtlmProvider
                self._token_provider = NtlmProvider(credentials.userName, credentials.password)
            else:
                browser_mode = kwargs.get('browser_mode', False)
                self._token_provider = SamlTokenProvider(self.url, credentials.userName, credentials.password, browser_mode)
        else:
            raise ValueError("Unknown credential type")

    def acquire_token_for_user(self, username, password, browser_mode=False):
        """
        Initializes a client to acquire a token via user credentials
        Status: deprecated!

        :param str password: The user password
        :param str username: Typically a UPN in the form of an email address
        :param bool browser_mode:
        """
        self._token_provider = SamlTokenProvider(url=self.url, username=username, password=password,
                                                 browser_mode=browser_mode)
        return self._token_provider.ensure_authentication_cookie()

    def acquire_token_for_app(self, client_id, client_secret):
        """
        Initializes a client to acquire a token via client credentials (SharePoint App-Only)

        Status: deprecated!

        :param str client_id: The OAuth client id of the calling application.
        :param str client_secret: Secret string that the application uses to prove its identity when requesting a token
        """
        self._token_provider = ACSTokenProvider(url=self.url, client_id=client_id, client_secret=client_secret)
        return self._token_provider.ensure_app_only_access_token()

    def authenticate_request(self, request):
        """
        Authenticate request
        :type request: office365.runtime.http.request_options.RequestOptions
        """
        if isinstance(self._token_provider, AuthenticationProvider):
            self._token_provider.authenticate_request(request)
        elif callable(self._token_provider):
            if self._cached_token is None:
                self._cached_token = self._token_provider()
            request.set_header('Authorization', _get_authorization_header(self._cached_token))
        else:
            raise ValueError("Authentication credentials are missing or invalid")
