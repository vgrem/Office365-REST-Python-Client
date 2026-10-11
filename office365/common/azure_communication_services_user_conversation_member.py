from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class AzureCommunicationServicesUserConversationMember(Entity):
    @property
    def azure_communication_services_id(self) -> Optional[str]:
        """Gets the azureCommunicationServicesId property"""
        return self.properties.get("azureCommunicationServicesId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AzureCommunicationServicesUserConversationMember"
