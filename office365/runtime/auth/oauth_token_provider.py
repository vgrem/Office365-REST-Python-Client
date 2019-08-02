import requests

from office365.runtime.auth.base_token_provider import BaseTokenProvider


class OAuthTokenProvider(BaseTokenProvider):
    """ OAuth security Token Service for O365"""

    def __init__(self, tenant):
        self.tenant = tenant
        self.AuthorityUrl = "https://login.microsoftonline.com/"
        self.TokenEndpoint = "/oauth2/token"
        self.error = None
        self.access_token = None

    def acquire_token(self, parameters):
        try:
            # url = "https://login.microsoftonline.com/{0}/oauth2/v2.0/token".format(self.tenant)
            url = "https://login.microsoftonline.com/{0}/oauth2/token".format(self.tenant)
            response = requests.post(url=url, headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                     data=parameters)
            self.access_token = response.json()
            return True
        except requests.exceptions.RequestException as e:
            self.error = "Error: {}".format(e)
            return False

    def get_authorization_header(self):
        return 'Bearer {0}'.format(self.access_token["access_token"])

    def acquire_token_password_type(self, resource, client_credentials, user_credentials):
        parameters = {
            'grant_type': 'password',
            'client_id': client_credentials['client_id'],
            'client_secret': client_credentials['client_secret'],
            'username': user_credentials['username'],
            'password': user_credentials['password'],
            'scope': 'user.read openid profile offline_access',
            'resource': resource
        }
        self.acquire_token(parameters)

    def get_last_error(self):
        return self.error
