from office365.runtime.auth.network_credential_context import NetworkCredentialContext

try:
    from requests_ntlm import HttpNtlmAuth
except ImportError:
    raise ImportError("To use NTLM authentication the package 'requests_ntlm' needs to be installed.")


class NTLMAuthenticationContext(NetworkCredentialContext):

    def __init__(self, username, password):
        """
            Provides NTLM authentication (intended for SharePoint On-Premises)

            Note: due to Outlook REST API v1.0 BasicAuth Deprecation
            (refer https://developer.microsoft.com/en-us/office/blogs/outlook-rest-api-v1-0-basicauth-deprecation/)
            NetworkCredentialContext class should be no longer utilized for Outlook REST API v1.0

            :type username: str
            :type password: str
        """
        super(NTLMAuthenticationContext, self).__init__(username, password)
        self.auth = HttpNtlmAuth(*self.userCredentials)

    def authenticate_request(self, request_options):
        request_options.auth = self.auth
