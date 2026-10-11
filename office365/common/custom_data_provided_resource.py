from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.extensions.custom.customextensionendpointconfiguration import (
        CustomExtensionEndpointConfiguration,
    )


class CustomDataProvidedResource(Entity):
    @property
    def notification_endpoint_configuration(self) -> CustomExtensionEndpointConfiguration:
        """Gets the notificationEndpointConfiguration property"""
        from office365.directory.extensions.custom.customextensionendpointconfiguration import (
            CustomExtensionEndpointConfiguration,
        )

        return self.properties.get("notificationEndpointConfiguration", CustomExtensionEndpointConfiguration())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CustomDataProvidedResource"
