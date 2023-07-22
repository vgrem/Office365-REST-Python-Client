import json
import sys

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
        self._authenticate = None
        self._cached_token = None

    def with_client_certificate(self, tenant, client_id, thumbprint, cert_path=None, private_key=None, scopes=None):
        """Initializes a client to acquire a token via certificate credentials

        :param str tenant: Tenant name, for example: contoso.onmicrosoft.com
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

        def _acquire_token():
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

        self.with_access_token(_acquire_token)
        return self

    def with_interactive(self, tenant, client_id, scopes=None):
        """
        Initializes a client to acquire a token interactively i.e. via a local browser.

        Prerequisite: In Azure Portal, configure the Redirect URI of your
        "Mobile and Desktop application" as ``http://localhost``.

        :param str tenant: Tenant name, for example: contoso.onmicrosoft.com
        :param str client_id: The OAuth client id of the calling application.
        :param list[str] or None scopes:  Scopes requested to access a protected API (a resource)
        """
        if scopes is None:
            resource = get_absolute_url(self.url)
            scopes = ["{url}/.default".format(url=resource)]

        def _acquire_token():
            import msal
            app = msal.PublicClientApplication(
                client_id,
                authority='https://login.microsoftonline.com/{0}'.format(tenant),
                client_credential=None
            )
            result = app.acquire_token_interactive(scopes=scopes)
            return TokenResponse.from_json(result)
        self.with_access_token(_acquire_token)
        return self

    def with_device_flow(self, tenant, client_id, scopes=None):
        """
        Obtain token by a device flow object, with customizable polling effect.

        :param str tenant: Tenant name, for example: contoso.onmicrosoft.com
        :param str client_id: The OAuth client id of the calling application.
        :param list[str] or None scopes:  Scopes requested to access a protected API (a resource)
        """
        if scopes is None:
            resource = get_absolute_url(self.url)
            scopes = ["{url}/.default".format(url=resource)]

        def _acquire_token():
            import msal
            app = msal.PublicClientApplication(
                client_id,
                authority='https://login.microsoftonline.com/{0}'.format(tenant),
                client_credential=None
            )

            flow = app.initiate_device_flow(scopes=scopes)
            if "user_code" not in flow:
                raise ValueError(
                    "Failed to create device flow: %s" % json.dumps(flow, indent=4))

            print(flow["message"])
            sys.stdout.flush()

            result = app.acquire_token_by_device_flow(flow)
            return TokenResponse.from_json(result)
        self.with_access_token(_acquire_token)
        return self

    def with_access_token(self, token_func):
        """
        Initializes a client to acquire a token from a callback

        :param () -> dict token_func: A callback
        """
        def _authenticate(request):
            if self._cached_token is None:
                self._cached_token = token_func()
            request.set_header('Authorization', _get_authorization_header(self._cached_token))
        self._authenticate = _authenticate

    def with_credentials(self, credentials, **kwargs):
        """
        Initializes a client to acquire a token via user or client credentials

        :param UserCredential or ClientCredential credentials:
        """
        if isinstance(credentials, ClientCredential):
            provider = ACSTokenProvider(self.url, credentials.clientId, credentials.clientSecret)
        elif isinstance(credentials, UserCredential):
            allow_ntlm = kwargs.get('allow_ntlm', False)
            if allow_ntlm:
                from office365.runtime.auth.providers.ntlm_provider import NtlmProvider
                provider = NtlmProvider(credentials.userName, credentials.password)
            else:
                browser_mode = kwargs.get('browser_mode', False)
                provider = SamlTokenProvider(self.url, credentials.userName, credentials.password, browser_mode)
        else:
            raise ValueError("Unknown credential type")

        def _authenticate(request):
            provider.authenticate_request(request)
        self._authenticate = _authenticate

    def acquire_token_for_user(self, username, password, browser_mode=False):
        """
        Initializes a client to acquire a token via user credentials
        Status: deprecated!

        :param str password: The user password
        :param str username: Typically a UPN in the form of an email address
        :param bool browser_mode:
        """
        provider = SamlTokenProvider(self.url, username, password, browser_mode)

        def _authenticate(request):
            provider.authenticate_request(request)
        self._authenticate = _authenticate
        return self

    def acquire_token_for_app(self, client_id, client_secret):
        """
        Initializes a client to acquire a token via client credentials (SharePoint App-Only)

        Status: deprecated!

        :param str client_id: The OAuth client id of the calling application.
        :param str client_secret: Secret string that the application uses to prove its identity when requesting a token
        """
        provider = ACSTokenProvider(self.url, client_id, client_secret)

        def _authenticate(request):
            provider.authenticate_request(request)
        self._authenticate = _authenticate
        return self

    def authenticate_request(self, request):
        """
        Authenticate request
        :type request: office365.runtime.http.request_options.RequestOptions
        """
        if self._authenticate is None:
            raise ValueError("Authentication credentials are missing or invalid")
        self._authenticate(request)
