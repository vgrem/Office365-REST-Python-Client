from datetime import datetime, timedelta
from office365.runtime.compat import urlparse, timezone


class STSProfile(object):

    def __init__(self, authority_url):
        """

        :type authority_url: str
        """
        self.authorityUrl = authority_url
        self.serviceUrl = 'https://login.microsoftonline.com'
        self.securityTokenServicePath = 'extSTS.srf'
        self.userRealmServicePath = 'GetUserRealm.srf'
        self.tokenIssuer = 'urn:federation:MicrosoftOnline'
        now = datetime.now(tz=timezone.utc)
        self.created = now.astimezone(timezone.utc).isoformat('T')[:-9] + 'Z'
        self.expires = (now + timedelta(minutes=10)).astimezone(timezone.utc).isoformat('T')[:-9] + 'Z'
        self.signInPage = '_forms/default.aspx?wa=wsignin1.0'

    @property
    def tenant(self):
        return urlparse(self.authorityUrl).netloc

    @property
    def security_token_service_url(self):
        return "/".join([self.serviceUrl, self.securityTokenServicePath])

    @property
    def signin_page_url(self):
        return "/".join([self.authorityUrl, self.signInPage])

    @property
    def user_realm_service_url(self):
        return '/'.join([self.serviceUrl, self.userRealmServicePath])
