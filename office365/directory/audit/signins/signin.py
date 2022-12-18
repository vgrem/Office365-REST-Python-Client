from office365.directory.audit.signins.status import SignInStatus
from office365.entity import Entity


class SignIn(Entity):
    """Details user and application sign-in activity for a tenant (directory).
    You must have an Azure AD Premium P1 or P2 license to download sign-in logs using the Microsoft Graph API.
    """

    @property
    def user_id(self):
        """
        ID of the user that initiated the sign-in. Supports $filter (eq operator only).
        :rtype: str or None
        """
        return self.properties.get("userId", None)

    @property
    def user_principal_name(self):
        """
        User principal name of the user that initiated the sign-in. Supports $filter (eq and startsWith operators only).
        :rtype: str or None
        """
        return self.properties.get("userPrincipalName", None)

    @property
    def status(self):
        """
        Sign-in status. Includes the error code and description of the error (in case of a sign-in failure).
        Supports $filter (eq operator only) on errorCode property.
        :rtype: str or None
        """
        return self.properties.get("status", SignInStatus())
