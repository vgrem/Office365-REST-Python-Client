from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.intune.print.task_definition import PrintTaskDefinition
    from office365.intune.print.task_status import PrintTaskStatus
    from office365.intune.print.task_trigger import PrintTaskTrigger


class PrintTask(Entity):
    @property
    def parent_url(self) -> Optional[str]:
        """Gets the parentUrl property"""
        return self.properties.get("parentUrl", None)

    @property
    def status(self) -> PrintTaskStatus:
        """Gets the status property"""
        from office365.intune.print.task_status import PrintTaskStatus

        return self.properties.get("status", PrintTaskStatus())

    @property
    def definition(self) -> PrintTaskDefinition:
        """Gets the definition property"""
        from office365.intune.print.task_definition import PrintTaskDefinition

        return self.properties.get(
            "definition", PrintTaskDefinition(self.context, ResourcePath("definition", self.resource_path))
        )

    @property
    def trigger(self) -> PrintTaskTrigger:
        """Gets the trigger property"""
        from office365.intune.print.task_trigger import PrintTaskTrigger

        return self.properties.get(
            "trigger", PrintTaskTrigger(self.context, ResourcePath("trigger", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PrintTask"
