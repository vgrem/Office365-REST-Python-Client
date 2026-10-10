from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.function import FunctionQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext
    from office365.sharepoint.viva.appsitecontext import AppSiteContext


class AppSiteContextUtility(Entity):
    @staticmethod
    def get_app_site_context_collection(context: ClientContext) -> ClientResult[ClientValueCollection[AppSiteContext]]:
        """GetAppSiteContextCollection operation."""
        from office365.sharepoint.apps.appsitecontextutility import (
            AppSiteContextUtility,
        )
        from office365.sharepoint.viva.appsitecontext import AppSiteContext

        return_type = ClientResult(context, ClientValueCollection[AppSiteContext]())
        qry = FunctionQuery(AppSiteContextUtility(context), "GetAppSiteContextCollection", [], return_type)
        context.add_query(qry)
        return return_type
