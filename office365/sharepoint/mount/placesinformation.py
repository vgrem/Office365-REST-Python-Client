from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.entity import Entity
from office365.sharepoint.entity_collection import EntityCollection
from office365.sharepoint.mount.placesuserentity import PlacesUserEntity

if TYPE_CHECKING:
    from office365.sharepoint.mount.placesentity import PlacesEntity


class PlacesInformation(Entity):
    @property
    def in_callers_drive(self) -> Optional[str]:
        """Gets the inCallersDrive property"""
        return self.properties.get("inCallersDrive", None)

    @property
    def places_count(self) -> Optional[str]:
        """Gets the placesCount property"""
        return self.properties.get("placesCount", None)

    @property
    def item_source_list_title(self) -> Optional[str]:
        """Gets the itemSourceListTitle property"""
        return self.properties.get("itemSourceListTitle", None)

    @property
    def item_source_path(self) -> Optional[str]:
        """Gets the itemSourcePath property"""
        return self.properties.get("itemSourcePath", None)

    @property
    def item_source_site_owner_identity(self) -> PlacesUserEntity:
        """Gets the itemSourceSiteOwnerIdentity property"""
        return self.properties.get("itemSourceSiteOwnerIdentity", PlacesUserEntity())

    @property
    def item_source_site_template_id(self) -> Optional[str]:
        """Gets the itemSourceSiteTemplateId property"""
        return self.properties.get("itemSourceSiteTemplateId", None)

    @property
    def item_source_site_title(self) -> Optional[str]:
        """Gets the itemSourceSiteTitle property"""
        return self.properties.get("itemSourceSiteTitle", None)

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.AddToOneDrive.PlacesInformation"

    @property
    def places(self) -> EntityCollection[PlacesEntity]:
        """Gets the places property"""
        from office365.sharepoint.mount.placesentity import PlacesEntity

        return self.properties.get(
            "places",
            EntityCollection[PlacesEntity](self.context, PlacesEntity, ResourcePath("places", self.resource_path)),
        )
