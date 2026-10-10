from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.client_result import ClientResult
from office365.runtime.queries.function import FunctionQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext
    from office365.sharepoint.sites.ngsprequestparams import NgspRequestParams


class NgspDataCollection(Entity):
    @staticmethod
    def get_ngsp_data(context: ClientContext, request: NgspRequestParams) -> ClientResult[str]:
        """GetNgspData operation.

        Args:
            request (NgspRequestParams):
                request parameter
        """
        from office365.sharepoint.news.ngspdatacollection import NgspDataCollection

        return_type = ClientResult(context, str())
        qry = FunctionQuery(NgspDataCollection(context), "GetNgspData", [request], return_type)
        context.add_query(qry)
        return return_type
