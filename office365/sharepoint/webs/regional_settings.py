from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.webs.time_zone import TimeZone, TimeZoneCollection


class RegionalSettings(BaseEntity):
    """Represents regional settings that are used on the server that is running SharePoint Server."""

    @property
    def date_format(self):
        """
        Gets the date format that is used on the server.

        :rtype: int or None
        """
        return self.properties.get("DateFormat", None)

    @property
    def locale_id(self):
        """
        Gets the locale identifier in use on the server.

        :rtype: int or None
        """
        return self.properties.get("LocaleId", None)

    @property
    def work_days(self):
        """
        Gets a number that represents the work days of Web site calendars.

        :rtype: int or None
        """
        return self.properties.get("WorkDays", None)

    @property
    def time_zone(self):
        """Gets the time zone that is used on the server."""
        return self.properties.get("TimeZone", TimeZone(self.context, ResourcePath("TimeZone", self.resource_path)))

    @property
    def time_zones(self):
        """Gets the collection of time zones used in a server farm."""
        return self.properties.get("TimeZones",
                                   TimeZoneCollection(self.context, ResourcePath("TimeZones", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "TimeZones": self.time_zones,
                "TimeZone": self.time_zone,
            }
            default_value = property_mapping.get(name, None)
        return super(RegionalSettings, self).get_property(name, default_value)
