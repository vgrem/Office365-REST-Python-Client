import requests
from office365.runtime.auth.base_token_provider import BaseTokenProvider
from office365.runtime.auth.tokenResponse import TokenResponse


class OAuthTokenProvider(BaseTokenProvider):
    """ OAuth token provider for AAD"""

    def __init__(self, tenant):
        self.authority_url = "https://login.microsoftonline.com/{tenant}".format(tenant=tenant)
        self.version = "v1.0"
        self.error = None
        self.token = TokenResponse()

    def acquire_token(self, parameters):
        try:
            token_url = "{authority}/oauth2/token".format(authority=self.authority_url)
            response = requests.post(url=token_url,
                                     headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                     data=parameters)
            self.token = TokenResponse.from_json(response.json())
            return self.token.is_valid
        except requests.exceptions.RequestException as e:
            self.error = "Error: {0}".format(e)
            return False

    def is_authenticated(self):
        return self.token and self.token.is_valid

    def get_authorization_header(self):
        return '{token_type} {access_token}'.format(token_type=self.token.tokenType, access_token=self.token.accessToken)

    def acquire_token_password_type(self, resource, client_id, user_credentials, scope):
        """
        Gets a token for a given resource via user credentials

        :param list[str] scope:
        :param str resource:
        :param str client_id:
        :param UserCredential user_credentials:
        :return: bool
        """
        token_parameters = {
            'grant_type': 'password',
            'client_id': client_id,
            'username': user_credentials.userName,
            'password': user_credentials.password,
            'scope': " ".join(scope),
            'resource': resource
        }
        return self.acquire_token(token_parameters)

    def get_last_error(self):
        return self.error
