from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.connection_info import ConnectionInfo
    from office365.externalconnectors.connector_type import ConnectorType


class ExternalOriginResourceConnector(Entity):
    @property
    def connection_info(self) -> ConnectionInfo:
        """Gets the connectionInfo property"""
        from office365.directory.connection_info import ConnectionInfo

        return self.properties.get("connectionInfo", ConnectionInfo())

    @property
    def connector_type(self) -> Optional[ConnectorType]:
        """Gets the connectorType property"""
        return self.properties.get("connectorType", None)

    @property
    def created_by(self) -> Optional[str]:
        """Gets the createdBy property"""
        return self.properties.get("createdBy", None)

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def modified_by(self) -> Optional[str]:
        """Gets the modifiedBy property"""
        return self.properties.get("modifiedBy", None)

    @property
    def modified_date_time(self) -> Optional[datetime]:
        """Gets the modifiedDateTime property"""
        return self.properties.get("modifiedDateTime", datetime.min)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ExternalOriginResourceConnector"
