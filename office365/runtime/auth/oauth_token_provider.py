import requests

from office365.runtime.auth.base_token_provider import BaseTokenProvider


class OAuthTokenProvider(BaseTokenProvider):
    """ OAuth security Token Service for O365"""

    def __init__(self, tenant, client_id, client_secret, user_name, password):
        self.tenant = tenant
        self.ResourceId = "https://graph.microsoft.com/"
        self.AuthorityUrl = "https://login.microsoftonline.com/"
        self.TokenEndpoint = "/oauth2/token"
        self.error = None
        self.access_token = None
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_name = user_name
        self.password = password
        self.scope = 'user.read openid profile offline_access https://graph.microsoft.com/Contacts.ReadWrite'

    def acquire_token(self):
        try:
            self.access_token = self.request_password_type()
            return True
        except requests.exceptions.RequestException as e:
            self.error = "Error: {}".format(e)
            return False

    def get_authorization_header(self):
        return 'Bearer {0}'.format(self.access_token["access_token"])

    def request_password_type(self):
        url = "https://login.microsoftonline.com/{0}/oauth2/v2.0/token".format(self.tenant)
        data = {
            'grant_type': 'password',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'username': self.user_name,
            'password': self.password,
            'scope': self.scope
        }

        response = requests.post(url=url, headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                 data=data)
        return response.json()
