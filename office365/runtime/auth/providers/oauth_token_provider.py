import requests
from office365.runtime.auth.base_token_provider import BaseTokenProvider
from office365.runtime.auth.tokenResponse import TokenResponse


class OAuthTokenProvider(BaseTokenProvider):
    """ OAuth token provider for AAD"""

    def __init__(self, tenant):
        self.tenant = tenant
        self.authority_url = "https://login.microsoftonline.com/"
        self.version = "v1.0"
        self.error = None
        self.token = None  # type: TokenResponse

    def acquire_token(self, parameters):
        try:
            url = "https://login.microsoftonline.com/{0}/oauth2/token".format(self.tenant)
            response = requests.post(url=url,
                                     headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                     data=parameters)
            self.token = TokenResponse.from_json(response.content)
            return self.token.is_valid
        except requests.exceptions.RequestException as e:
            self.error = "Error: {}".format(e)
            return False

    def is_authenticated(self):
        return self.token and self.token.is_valid

    def get_authorization_header(self):
        return '{token_type} {access_token}'.format(token_type=self.token.tokenType, access_token=self.token.accessToken)

    def acquire_token_password_type(self, resource, client_credentials, user_credentials):
        token_parameters = {
            'grant_type': 'password',
            'client_id': client_credentials['client_id'],
            'client_secret': client_credentials['client_secret'],
            'username': user_credentials['username'],
            'password': user_credentials['password'],
            'scope': 'user.read openid profile offline_access',
            'resource': resource
        }
        self.acquire_token(token_parameters)

    def get_last_error(self):
        return self.error
