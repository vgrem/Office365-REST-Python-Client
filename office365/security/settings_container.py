from __future__ import annotations

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath
from office365.security.auto_auditing_configuration import AutoAuditingConfiguration


class SettingsContainer(Entity):
    @property
    def auto_auditing_configuration(self) -> AutoAuditingConfiguration:
        """Gets the autoAuditingConfiguration property"""
        return self.properties.get(
            "autoAuditingConfiguration",
            AutoAuditingConfiguration(self.context, ResourcePath("autoAuditingConfiguration", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.SettingsContainer"
