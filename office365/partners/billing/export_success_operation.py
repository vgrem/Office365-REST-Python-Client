from __future__ import annotations

from office365.entity import Entity
from office365.partners.billing.manifest import Manifest
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.pollable import PollableOperation


class ExportSuccessOperation(PollableOperation, Entity):
    @property
    def resource_location(self) -> Manifest:
        """Gets the resourceLocation property"""
        return self.properties.get(
            "resourceLocation", Manifest(self.context, ResourcePath("resourceLocation", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.partners.billing.ExportSuccessOperation"
