import datetime

from office365.directory.audit.signins.location import SignInLocation
from office365.directory.audit.signins.status import SignInStatus
from office365.entity import Entity
from office365.intune.devices.detail import DeviceDetail


class SignIn(Entity):
    """Details user and application sign-in activity for a tenant (directory).
    You must have an Azure AD Premium P1 or P2 license to download sign-in logs using the Microsoft Graph API.
    """

    @property
    def app_display_name(self):
        """
        App name displayed in the Azure Portal.
        :rtype: str
        """
        return self.properties.get("appDisplayName", None)

    @property
    def app_id(self):
        """
        Unique GUID representing the app ID in the Azure Active Directory.
        :rtype: str
        """
        return self.properties.get("appId", None)

    @property
    def client_app_used(self):
        """
        Identifies the client used for the sign-in activity. Modern authentication clients include Browser, modern
        clients. Legacy authentication clients include Exchange ActiveSync, IMAP, MAPI, SMTP, POP, and other clients.
        :rtype: str
        """
        return self.properties.get("clientAppUsed", None)

    @property
    def correlation_id(self):
        """
        The request ID sent from the client when the sign-in is initiated; used to troubleshoot sign-in activity.
        :rtype: str
        """
        return self.properties.get("correlationId", None)

    @property
    def created_datetime(self):
        """	Date and time (UTC) the sign-in was initiated. """
        return self.properties.get('createdDateTime', datetime.datetime.min)

    @property
    def device_detail(self):
        """Device information from where the sign-in occurred; includes device ID, operating system, and browser.
        Supports $filter (eq and startsWith operators only) on browser and operatingSytem properties."""
        return self.properties.get("deviceDetail", DeviceDetail())

    @property
    def ip_address(self):
        """
        IP address of the client used to sign in.
        :rtype: str
        """
        return self.properties.get("ipAddress", None)

    @property
    def is_interactive(self):
        """
        Indicates if a sign-in is interactive or not.
        :rtype: bool or None
        """
        return self.properties.get("isInteractive", None)

    @property
    def location(self):
        """
        Provides the city, state, and country code where the sign-in originated.
        Supports $filter (eq and startsWith operators only) on city, state, and countryOrRegion properties.
        """
        return self.properties.get("status", SignInLocation())

    @property
    def resource_display_name(self):
        """
        Name of the resource the user signed into.
        :rtype: str or None
        """
        return self.properties.get("resourceDisplayName", None)

    @property
    def resource_id(self):
        """
        ID of the resource that the user signed into.
        :rtype: str or None
        """
        return self.properties.get("resourceId", None)

    @property
    def risk_detail(self):
        """
        Provides the 'reason' behind a specific state of a risky user, sign-in or a risk event.
        :rtype: str or None
        """
        return self.properties.get("riskDetail", None)

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
                "createdDateTime": self.created_datetime,
                "deviceDetail": self.device_detail
            }
            default_value = property_mapping.get(name, None)
        return super(SignIn, self).get_property(name, default_value)
