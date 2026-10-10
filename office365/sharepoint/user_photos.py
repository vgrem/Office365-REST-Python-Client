from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext


class UserPhotos(Entity):
    @property
    def settings(self) -> Optional[str]:
        """Gets the Settings property"""
        return self.properties.get("Settings", None)

    @staticmethod
    def set_settings(context: ClientContext, settings: str) -> ClientResult[str]:
        """SetSettings operation.

        Args:
            settings (str):
                settings parameter
        """
        return_type = ClientResult(context, str())
        qry = ServiceOperationQuery(
            UserPhotos(context), "SetSettings", None, {"settings": settings}, None, return_type, True
        )
        context.add_query(qry)
        return return_type
