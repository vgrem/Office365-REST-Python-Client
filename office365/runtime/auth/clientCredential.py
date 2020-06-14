class ClientCredential(object):

    def __init__(self, client_id, client_secret):
        """
        Client credentials

        :type client_secret: str
        :type client_id: str
        """
        self.clientId = client_id
        self.clientSecret = client_secret
