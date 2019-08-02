import requests

import office365.logger
from office365.runtime.auth.base_token_provider import BaseTokenProvider


class ACSTokenProvider(BaseTokenProvider, office365.logger.LoggerContext):
    """ Provider to acquire the access token from a Microsoft Azure Access Control Service (ACS)"""

    def __init__(self, url, client_id, client_secret):
        self.url = url
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_url = None
        self.access_token = None
        self.error = None
        self.SharePointPrincipal = "00000003-0000-0ff1-ce00-000000000000"

    def acquire_token(self):
        try:
            realm = self.get_realm_from_target_url()
            try:
                from urlparse import urlparse  # Python 2.X
            except ImportError:
                from urllib.parse import urlparse  # Python 3+
            url_info = urlparse(self.url)
            self.access_token = self.get_app_only_access_token(url_info.hostname, realm)
            return True
        except requests.exceptions.RequestException as e:
            self.error = "Error: {}".format(e)
            return False

    def get_realm_from_target_url(self):
        response = requests.head(url=self.url, headers={'Authorization': 'Bearer'})
        return self.process_realm_response(response)

    def get_app_only_access_token(self, target_host, target_realm):
        resource = self.get_formatted_principal(self.SharePointPrincipal, target_host, target_realm)
        client_id = self.get_formatted_principal(self.client_id, None, target_realm)
        sts_url = self.get_security_token_service_url(target_realm)
        oauth2_request = self.create_access_token_request(client_id, self.client_secret, resource)
        response = requests.post(url=sts_url, headers={'Content-Type': 'application/x-www-form-urlencoded'}, data=oauth2_request)
        return response.json()

    @staticmethod
    def process_realm_response(response):
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

    @staticmethod
    def create_access_token_request(client_id, client_secret, scope):
        data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': scope,
            'resource': scope
        }
        return data

    def get_authorization_header(self):
        return 'Bearer {0}'.format(self.access_token["access_token"])

    def get_last_error(self):
        return self.error
