from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.sitedesigns.metadata import SiteDesignMetadata


class DesignPackageMenuContents(Entity):
    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Utilities.WebTemplateExtensions.DesignPackageMenuContents"

    @property
    def hidden_design_packages(self) -> Optional[int]:
        """Gets the HiddenDesignPackages property"""
        return self.properties.get("HiddenDesignPackages", None)

    @property
    def site_designs(self) -> ClientValueCollection[SiteDesignMetadata]:
        """Gets the SiteDesigns property"""
        from office365.sharepoint.sitedesigns.metadata import SiteDesignMetadata

        return self.properties.get("SiteDesigns", ClientValueCollection[SiteDesignMetadata](SiteDesignMetadata))
