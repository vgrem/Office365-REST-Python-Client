from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.compliance.microsoftedgechannel import (
        MicrosoftEdgeChannel,
    )


class MacOSMicrosoftEdgeApp(Entity):
    @property
    def channel(self) -> MicrosoftEdgeChannel:
        """Gets the channel property"""
        from office365.intune.devices.compliance.microsoftedgechannel import (
            MicrosoftEdgeChannel,
        )

        return self.properties.get("channel", MicrosoftEdgeChannel.dev)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MacOSMicrosoftEdgeApp"
