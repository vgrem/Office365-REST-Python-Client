from office365.runtime.auth.network_credential_context import NetworkCredentialContext

try:
    from requests_ntlm import HttpNtlmAuth
except ImportError:
    raise ImportError("To use NTLM authentication the package 'requests_ntlm' needs to be installed")


class NTLMAuthenticationContext(NetworkCredentialContext):
    """Provides NTLM authentication"""

    def __init__(self, username, password):
        super(NTLMAuthenticationContext, self).__init__(username, password)
        self.auth = HttpNtlmAuth(*self.userCredentials)

    def authenticate_request(self, request_options):
        request_options.auth = self.auth
