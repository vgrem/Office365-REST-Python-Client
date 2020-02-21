import datetime


class STSProfile(object):

    def __init__(self, authority_url):
        self.authorityUrl = authority_url
        self.serviceUrl = 'https://login.microsoftonline.com'
        self.securityTokenServicePath = 'extSTS.srf'
        self.userRealmServicePath = 'GetUserRealm.srf'
        self.federationTokenIssuer = 'urn:federation:MicrosoftOnline'
        self.created = datetime.datetime.now()
        self.expires = self.created + datetime.timedelta(minutes=10)
        self.signInPage = '_forms/default.aspx?wa=wsignin1.0'

    @property
    def securityTokenServiceUrl(self):
        return "/".join([self.serviceUrl, self.securityTokenServicePath])

    @property
    def signInPageUrl(self):
        return "/".join([self.authorityUrl, self.signInPage])

    @property
    def userRealmServiceUrl(self):
        return '/'.join([self.serviceUrl, self.userRealmServicePath])
