from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity


class PushNotificationSubscriber(BaseEntity):
    """Represents a push notification subscriber over a site."""

    @property
    def custom_args(self):
        """Gets the custom arguments specified by the app.

        :rtype: str
        """
        return self.properties.get("CustomArgs", None)

    @property
    def service_token(self):
        """Specifies the delivery channel URI for push notifications. It must not be null. It must not be empty.

        :rtype: str
        """
        return self.properties.get("ServiceToken", None)

    @service_token.setter
    def service_token(self, value):
        """
        Specifies the delivery channel URI for push notifications. It must not be null. It must not be empty.

        :type value: str
        """
        self.set_property("ServiceToken", value)

    @property
    def device_app_instance_id(self):
        """Specifies a device app instance identifier.

        :rtype: str
        """
        return self.properties.get("DeviceAppInstanceId", None)

    @property
    def last_modified_time_stamp(self):
        """Specifies the time and date when the subscriber was last updated.

        :rtype: str
        """
        return self.properties.get("LastModifiedTimeStamp", None)

    @property
    def registration_time_stamp(self):
        """Specifies the time and date when the subscriber registered for push notifications.

        :rtype: str
        """
        return self.properties.get("RegistrationTimeStamp", None)

    @property
    def user(self):
        """Gets the SharePoint user who created this subscriber."""
        from office365.sharepoint.principal.users.user import User
        return self.properties.get("User", User(self.context, ResourcePath("user", self.resource_path)))
