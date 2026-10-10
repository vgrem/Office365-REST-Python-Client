from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class WorkflowVersion(Entity):
    @property
    def version_number(self) -> Optional[int]:
        """Gets the versionNumber property"""
        return self.properties.get("versionNumber", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.identityGovernance.WorkflowVersion"
