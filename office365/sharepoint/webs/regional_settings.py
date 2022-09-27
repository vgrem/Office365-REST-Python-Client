from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.sites.language_collection import LanguageCollection
from office365.sharepoint.webs.time_zone import TimeZone, TimeZoneCollection


class RegionalSettings(BaseEntity):
    """Represents regional settings that are used on the server that is running SharePoint Server."""

    @property
    def collation(self):
        """
        Specifies the collation order of the site (2), which indicates an additional sorting order that SHOULD
        be processed by any back-end database server associated with the site (2). The collation method is an
        implementation-specific capability of the front-end Web server and back-end database server.

        :rtype: int or None
        """
        return self.properties.get("Collation", None)

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

    @property
    def installed_languages(self):
        return self.properties.get("InstalledLanguages",
                                   LanguageCollection(self.context,
                                                      ResourcePath("InstalledLanguages", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "TimeZones": self.time_zones,
                "TimeZone": self.time_zone,
                "InstalledLanguages": self.installed_languages
            }
            default_value = property_mapping.get(name, None)
        return super(RegionalSettings, self).get_property(name, default_value)
