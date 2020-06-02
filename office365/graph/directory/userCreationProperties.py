from office365.runtime.client_value_object import ClientValueObject


class UserCreationProperties(ClientValueObject):
    def __init__(self, principal_name, password_profile):
        super(UserCreationProperties, self).__init__()
        self.userPrincipalName = principal_name
        self.passwordProfile = password_profile
        self.mailNickname = None
        self.displayName = principal_name.split("@")[0]
        self.accountEnabled = False
