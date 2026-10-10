from __future__ import annotations

from typing import Optional

from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.documents.countbydate import CountByDate
from office365.sharepoint.entity import Entity


class RecentList(Entity):
    @property
    def color(self) -> Optional[str]:
        """Gets the color property"""
        return self.properties.get("color", None)

    @property
    def created_by_name(self) -> Optional[str]:
        """Gets the createdByName property"""
        return self.properties.get("createdByName", None)

    @property
    def created_by_upn(self) -> Optional[str]:
        """Gets the createdByUpn property"""
        return self.properties.get("createdByUpn", None)

    @property
    def created_date(self) -> Optional[str]:
        """Gets the createdDate property"""
        return self.properties.get("createdDate", None)

    @property
    def icon(self) -> Optional[str]:
        """Gets the icon property"""
        return self.properties.get("icon", None)

    @property
    def last_modified_date(self) -> Optional[str]:
        """Gets the lastModifiedDate property"""
        return self.properties.get("lastModifiedDate", None)

    @property
    def last_view_date(self) -> Optional[int]:
        """Gets the lastViewDate property"""
        return self.properties.get("lastViewDate", None)

    @property
    def lastview_date_time(self) -> Optional[str]:
        """Gets the lastviewDateTime property"""
        return self.properties.get("lastviewDateTime", None)

    @property
    def list_id(self) -> Optional[str]:
        """Gets the listId property"""
        return self.properties.get("listId", None)

    @property
    def list_title(self) -> Optional[str]:
        """Gets the listTitle property"""
        return self.properties.get("listTitle", None)

    @property
    def list_url(self) -> Optional[str]:
        """Gets the listUrl property"""
        return self.properties.get("listUrl", None)

    @property
    def list_view_counts(self) -> ClientValueCollection[CountByDate]:
        """Gets the listViewCounts property"""
        return self.properties.get("listViewCounts", ClientValueCollection(CountByDate))

    @property
    def should_remove(self) -> Optional[bool]:
        """Gets the shouldRemove property"""
        return self.properties.get("shouldRemove", None)

    @property
    def site_color(self) -> Optional[str]:
        """Gets the siteColor property"""
        return self.properties.get("siteColor", None)

    @property
    def site_id(self) -> Optional[str]:
        """Gets the siteId property"""
        return self.properties.get("siteId", None)

    @property
    def site_title(self) -> Optional[str]:
        """Gets the siteTitle property"""
        return self.properties.get("siteTitle", None)

    @property
    def site_url(self) -> Optional[str]:
        """Gets the siteUrl property"""
        return self.properties.get("siteUrl", None)

    @property
    def template_type_id(self) -> Optional[str]:
        """Gets the templateTypeId property"""
        return self.properties.get("templateTypeId", None)

    @property
    def web_id(self) -> Optional[str]:
        """Gets the webId property"""
        return self.properties.get("webId", None)

    @property
    def web_template_configuration(self) -> Optional[str]:
        """Gets the webTemplateConfiguration property"""
        return self.properties.get("webTemplateConfiguration", None)

    @property
    def lastview_datetime(self) -> Optional[str]:
        """Gets the lastviewDateTime property"""
        return self.properties.get("lastviewDateTime", None)
