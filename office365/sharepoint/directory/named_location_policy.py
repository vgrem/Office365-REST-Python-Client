from __future__ import annotations

from typing import Optional

from office365.runtime.types.collections import StringCollection
from office365.sharepoint.entity import Entity


class NamedLocationPolicy(Entity):
    @property
    def countries_and_regions(self) -> StringCollection:
        """Gets the countriesAndRegions property"""
        return self.properties.get("countriesAndRegions", StringCollection())

    @property
    def country_lookup_method(self) -> Optional[str]:
        """Gets the countryLookupMethod property"""
        return self.properties.get("countryLookupMethod", None)

    @property
    def created_date_time(self) -> Optional[str]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def id_(self) -> Optional[str]:
        """Gets the id property"""
        return self.properties.get("id", None)

    @property
    def include_unknown_countries_and_regions(self) -> Optional[bool]:
        """Gets the includeUnknownCountriesAndRegions property"""
        return self.properties.get("includeUnknownCountriesAndRegions", None)

    @property
    def ip_ranges(self) -> Optional[str]:
        """Gets the ipRanges property"""
        return self.properties.get("ipRanges", None)

    @property
    def is_trusted(self) -> Optional[bool]:
        """Gets the isTrusted property"""
        return self.properties.get("isTrusted", None)

    @property
    def modified_date_time(self) -> Optional[str]:
        """Gets the modifiedDateTime property"""
        return self.properties.get("modifiedDateTime", None)

    @property
    def odata_type(self) -> Optional[str]:
        """Gets the odataType property"""
        return self.properties.get("odataType", None)

    @property
    def entity_type_name(self) -> str:
        return "SP.Directory.NamedLocationPolicy"

    @property
    def created_datetime(self) -> Optional[str]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", None)

    @property
    def id(self) -> Optional[str]:
        """Gets the id property"""
        return self.properties.get("id", None)

    @property
    def modified_datetime(self) -> Optional[str]:
        """Gets the modifiedDateTime property"""
        return self.properties.get("modifiedDateTime", None)
