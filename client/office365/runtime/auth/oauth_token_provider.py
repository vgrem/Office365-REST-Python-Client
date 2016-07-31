from client.office365.runtime import BaseTokenProvider


class OAuthTokenProvider(BaseTokenProvider):
    """ OAuth security Token Service for O365"""

    def acquire_token(self):
        pass
