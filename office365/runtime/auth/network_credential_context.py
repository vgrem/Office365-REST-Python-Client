from office365.runtime.auth.base_authentication_context import BaseAuthenticationContext


class NetworkCredentialContext(BaseAuthenticationContext):
    """Provides credentials for password-based authentication schemes such as basic authentication"""

    def __init__(self, username, password):
        super(NetworkCredentialContext, self).__init__()
        self.userCredentials = (username, password)

    def authenticate_request(self, request_options):
        request_options.auth = self.userCredentials
