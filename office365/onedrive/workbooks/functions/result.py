from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class WorkbookFunctionResult(Entity):
    """"""

    @property
    def value(self):
        return self.properties.get("value", None)

    @property
    def error(self) -> Optional[str]:
        """Gets the error property"""
        return self.properties.get("error", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WorkbookFunctionResult"
