from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.client_result import ClientResult
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.types.collections import StringCollection
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext


class OneDriveItemCollection(Entity):
    @staticmethod
    def get_smart_cache_data(context: ClientContext, names: list[str]) -> ClientResult[StringCollection]:
        """GetSmartCacheData operation.

        Args:
            names (list[str]):
                names parameter
        """
        from office365.sharepoint.mount.onedriveitemcollection import (
            OneDriveItemCollection,
        )

        return_type = ClientResult(context, StringCollection())
        qry = FunctionQuery(OneDriveItemCollection(context), "GetSmartCacheData", [StringCollection(names)], return_type)
        context.add_query(qry)
        return return_type
