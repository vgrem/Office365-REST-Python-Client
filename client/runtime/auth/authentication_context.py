from client.runtime.auth.saml_token_provider import SamlTokenProvider


class AuthenticationContext(object):
    """SharePoint Online Authentication Context"""

    def __init__(self, url):
        self.url = url
        self.provider = None

    def acquire_token_for_user(self, username, password):
        """Acquire user token"""
        self.provider = SamlTokenProvider(self.url, username, password)
        return self.provider.acquire_token()

    def authenticate_request(self, headers):
        """Authenticate request"""
        headers['Cookie'] = self.provider.get_authentication_cookie()

    def get_last_error(self):
        return self.provider.get_last_error()
