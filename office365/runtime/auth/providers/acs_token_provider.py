import requests

import office365.logger
from office365.runtime.auth.authentication_provider import AuthenticationProvider
from office365.runtime.auth.token_response import TokenResponse
from office365.runtime.compat import urlparse


class ACSTokenProvider(AuthenticationProvider, office365.logger.LoggerContext):

    def __init__(self, url, client_id, client_secret):
        """
        Provider to acquire the access token from a Microsoft Azure Access Control Service (ACS)

        :param str client_id: The OAuth client id of the calling application.
        :param str client_secret: Secret string that the application uses to prove its identity when requesting a token
        :param str url: SharePoint web or site url
        """
        self.url = url
        self.redirect_url = None
        self.error = None
        self.SharePointPrincipal = "00000003-0000-0ff1-ce00-000000000000"
        self._client_id = client_id
        self._client_secret = client_secret
        self._cached_token = None

    def authenticate_request(self, request):
        """
        :type request: office365.runtime.http.request_options.RequestOptions
        """
        self.ensure_app_only_access_token()
        request.set_header('Authorization', self._get_authorization_header())

    def ensure_app_only_access_token(self):
        if self._cached_token is None:
            self._cached_token = self.get_app_only_access_token()
        return self._cached_token and self._cached_token.is_valid

    def get_app_only_access_token(self):
        """
        Retrieves an app-only access token from ACS
        """
        try:
            realm = self._get_realm_from_target_url()
            url_info = urlparse(self.url)
            return self._get_app_only_access_token(url_info.hostname, realm)
        except requests.exceptions.RequestException as e:
            self.error = e.response.text if e.response is not None else "Acquire app-only access token failed."
            raise ValueError(self.error)

    def _get_app_only_access_token(self, target_host, target_realm):
        """
        Retrieves an app-only access token from ACS to call the specified principal
        at the specified targetHost. The targetHost must be registered for target principal.

        :param str target_host: Url authority of the target principal
        :param str target_realm: Realm to use for the access token's nameid and audience
        """
        resource = self.get_formatted_principal(self.SharePointPrincipal, target_host, target_realm)
        principal_id = self.get_formatted_principal(self._client_id, None, target_realm)
        sts_url = self.get_security_token_service_url(target_realm)
        oauth2_request = {
            'grant_type': 'client_credentials',
            'client_id': principal_id,
            'client_secret': self._client_secret,
            'scope': resource,
            'resource': resource
        }
        response = requests.post(url=sts_url, headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                 data=oauth2_request)
        response.raise_for_status()
        return TokenResponse.from_json(response.json())

    def _get_realm_from_target_url(self):
        """Get the realm for the URL"""
        response = requests.head(url=self.url, headers={'Authorization': 'Bearer'})
        return self.process_realm_response(response)

    @staticmethod
    def process_realm_response(response):
        """
        :type response: requests.Response
        """
        header_key = "WWW-Authenticate"
        if header_key in response.headers:
            auth_values = response.headers[header_key].split(",")
            bearer = auth_values[0].split("=")
            return bearer[1].replace('"', '')
        return None

    @staticmethod
    def get_formatted_principal(principal_name, host_name, realm):
        if host_name:
            return "{0}/{1}@{2}".format(principal_name, host_name, realm)
        return "{0}@{1}".format(principal_name, realm)

    @staticmethod
    def get_security_token_service_url(realm):
        return "https://accounts.accesscontrol.windows.net/{0}/tokens/OAuth/2".format(realm)

    def _get_authorization_header(self):
        return 'Bearer {0}'.format(self._cached_token.accessToken)

    def get_last_error(self):
        return self.error
