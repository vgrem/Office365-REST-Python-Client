from office365.directory.audit.signins.location import SignInLocation
from office365.directory.audit.signins.status import SignInStatus
from office365.entity import Entity
from office365.intune.devices.detail import DeviceDetail


class SignIn(Entity):
    """Details user and application sign-in activity for a tenant (directory).
    You must have an Azure AD Premium P1 or P2 license to download sign-in logs using the Microsoft Graph API.
    """

    @property
    def device_detail(self):
        """Device information from where the sign-in occurred; includes device ID, operating system, and browser.
        Supports $filter (eq and startsWith operators only) on browser and operatingSytem properties."""
        return self.properties.get("deviceDetail", DeviceDetail())

    @property
    def location(self):
        """
        Provides the city, state, and country code where the sign-in originated.
        Supports $filter (eq and startsWith operators only) on city, state, and countryOrRegion properties.
        """
        return self.properties.get("status", SignInLocation())

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

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "deviceDetail": self.device_detail
            }
            default_value = property_mapping.get(name, None)
        return super(SignIn, self).get_property(name, default_value)
