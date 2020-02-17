class UserRealmInfo(object):

    def __init__(self, auth_url, federated):
        self.STSAuthUrl = auth_url
        self.IsFederated = federated

