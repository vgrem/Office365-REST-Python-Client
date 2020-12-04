from office365.runtime.auth.authentication_provider import AuthenticationProvider


class OAuthTokenProvider(AuthenticationProvider):
    """ OAuth token provider for AAD"""

    def __init__(self, token_func=None):
        self._error = None
        self._token_func = token_func
        self._cached_token = None

    def authenticate_request(self, request):
        """
        :type request: office365.runtime.http.request_options.RequestOptions
        """
        if self._cached_token is None:
            self._cached_token = self._token_func()
        request.set_header('Authorization', self._get_authorization_header())

    def _get_authorization_header(self):
        return '{token_type} {access_token}'.format(token_type=self._cached_token.tokenType,
                                                    access_token=self._cached_token.accessToken)

    def get_last_error(self):
        return self._error
