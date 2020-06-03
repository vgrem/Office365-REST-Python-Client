from office365.graph.directory.passwordProfile import PasswordProfile
from office365.runtime.client_value_object import ClientValueObject


class UserProfile(ClientValueObject):
    def __init__(self, principal_name, password, display_name=None, account_enabled=False):
        """
        User profile

        :type principal_name: str
        :type password: str
        :type display_name: str
        :type account_enabled: bool
        """
        super(UserProfile, self).__init__()
        self.userPrincipalName = principal_name
        self.passwordProfile = PasswordProfile(password)
        self.mailNickname = principal_name.split("@")[0]
        self.displayName = display_name or principal_name.split("@")[0]
        self.accountEnabled = account_enabled
