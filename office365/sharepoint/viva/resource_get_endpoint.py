from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.viva.resource_link import VivaResourceLink


class VivaResourceGetEndpoint(Entity):
    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.EmployeeEngagement.VivaResourceGetEndpoint"

    @property
    def company_links(self) -> ClientValueCollection[VivaResourceLink]:
        """Gets the CompanyLinks property"""
        from office365.sharepoint.viva.resource_link import VivaResourceLink

        return self.properties.get("CompanyLinks", ClientValueCollection[VivaResourceLink](VivaResourceLink))
