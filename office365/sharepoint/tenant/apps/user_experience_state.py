from __future__ import annotations

from typing import Optional

from typing_extensions import Self

from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity


class UserExperienceState(Entity):
    """"""

    @property
    def flags(self) -> Optional[int]:
        """Gets the Flags property"""
        return self.properties.get("Flags", None)

    def set_flag(self, flag: int, reset: bool) -> Self:
        """SetFlag operation.

        Args:
            flag (int):
                flag parameter
            reset (bool):
                reset parameter
        """
        qry = ServiceOperationQuery(self, "SetFlag", None, {"flag": flag, "reset": reset}, None, None)
        self.context.add_query(qry)
        return self
