from office365.directory.identities.authentication_configuration_base import ApiAuthenticationConfigurationBase


class BasicAuthentication(ApiAuthenticationConfigurationBase):
    """
    Represents configuration for using HTTP Basic authentication, which entails a username and password, in an API call.
     The username and password is sent as the Authorization header as Basic {value} where value is
     base 64 encoded version of username:password.
    """

    def __init__(self, username=None, password=None):
        super(BasicAuthentication, self).__init__()
        self.username = username
        self.password = password
