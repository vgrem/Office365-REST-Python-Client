from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.management.exchangeconnectors.status import (
        DeviceManagementExchangeConnectorStatus,
    )
    from office365.intune.devices.management.exchangeconnectors.type import (
        DeviceManagementExchangeConnectorType,
    )


class DeviceManagementExchangeConnector(Entity):
    @property
    def connector_server_name(self) -> Optional[str]:
        """Gets the connectorServerName property"""
        return self.properties.get("connectorServerName", None)

    @property
    def exchange_alias(self) -> Optional[str]:
        """Gets the exchangeAlias property"""
        return self.properties.get("exchangeAlias", None)

    @property
    def exchange_connector_type(self) -> DeviceManagementExchangeConnectorType:
        """Gets the exchangeConnectorType property"""
        from office365.intune.devices.management.exchangeconnectors.type import (
            DeviceManagementExchangeConnectorType,
        )

        return self.properties.get("exchangeConnectorType", DeviceManagementExchangeConnectorType.onPremises)

    @property
    def exchange_organization(self) -> Optional[str]:
        """Gets the exchangeOrganization property"""
        return self.properties.get("exchangeOrganization", None)

    @property
    def last_sync_date_time(self) -> Optional[datetime]:
        """Gets the lastSyncDateTime property"""
        return self.properties.get("lastSyncDateTime", datetime.min)

    @property
    def primary_smtp_address(self) -> Optional[str]:
        """Gets the primarySmtpAddress property"""
        return self.properties.get("primarySmtpAddress", None)

    @property
    def server_name(self) -> Optional[str]:
        """Gets the serverName property"""
        return self.properties.get("serverName", None)

    @property
    def status(self) -> DeviceManagementExchangeConnectorStatus:
        """Gets the status property"""
        from office365.intune.devices.management.exchangeconnectors.status import (
            DeviceManagementExchangeConnectorStatus,
        )

        return self.properties.get("status", DeviceManagementExchangeConnectorStatus.none)

    @property
    def version(self) -> Optional[str]:
        """Gets the version property"""
        return self.properties.get("version", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DeviceManagementExchangeConnector"
