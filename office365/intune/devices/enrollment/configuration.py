import datetime

from office365.entity import Entity


class DeviceEnrollmentConfiguration(Entity):
    """The Base Class of Device Enrollment Configuration"""

    @property
    def created_datetime(self):
        """
        Created date time in UTC of the device enrollment configuration
        """
        return self.properties.get("createdDateTime", datetime.datetime.min)

    @property
    def display_name(self):
        """
        The display name of the device enrollment configuration
        :rtype: str
        """
        return self.properties.get("displayName", None)

    def get_property(self, name, default_value=None):
        return super(DeviceEnrollmentConfiguration, self).get_property(name, default_value)
