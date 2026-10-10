from __future__ import annotations

from office365.runtime.client_result import ClientResult
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.entity import Entity


class RecentFileCollection(Entity):
    def __init__(self, context):
        super().__init__(context, ResourcePath("SP.RecentFileCollection"))

    @staticmethod
    def get_recent_files(context: ClientContext, top: int) -> ClientResult[str]:
        return_type = ClientResult(context, str())
        payload = {"top": top}
        binding_type = RecentFileCollection(context)
        qry = ServiceOperationQuery(binding_type, "GetRecentFiles", payload, None, None, return_type, True)
        context.add_query(qry)
        return return_type

    @staticmethod
    def delta_sync(context: ClientContext, top: int, start_datetime: str, skip_token: str) -> ClientResult[str]:
        """DeltaSync operation.

        Args:
            top (int):
                top parameter
            start_datetime (str):
                startDateTime parameter
            skip_token (str):
                skipToken parameter
        """
        from office365.sharepoint.files.recent_file_collection import (
            RecentFileCollection,
        )

        return_type = ClientResult(context, str())
        qry = FunctionQuery(RecentFileCollection(context), "DeltaSync", [top, start_datetime, skip_token], return_type)
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_recommendations(context: ClientContext, top: int) -> ClientResult[str]:
        """GetRecommendations operation.

        Args:
            top (int):
                top parameter
        """
        from office365.sharepoint.files.recent_file_collection import (
            RecentFileCollection,
        )

        return_type = ClientResult(context, str())
        qry = FunctionQuery(RecentFileCollection(context), "GetRecommendations", [top], return_type)
        context.add_query(qry)
        return return_type
