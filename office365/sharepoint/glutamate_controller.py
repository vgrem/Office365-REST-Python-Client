from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext
    from office365.sharepoint.sitedesigns.thread_engagement_data import (
        ThreadEngagementData,
    )


class GlutamateController(Entity):
    @staticmethod
    def get_thread_engagement_data(
        context: ClientContext, thread_ids: list[str]
    ) -> ClientResult[ClientValueCollection[ThreadEngagementData]]:
        """GetThreadEngagementData operation.

        Args:
            thread_ids (list[str]):
                threadIds parameter
        """
        from office365.sharepoint.sitedesigns.thread_engagement_data import (
            ThreadEngagementData,
        )

        return_type = ClientResult(context, ClientValueCollection[ThreadEngagementData]())
        qry = ServiceOperationQuery(
            GlutamateController(context),
            "GetThreadEngagementData",
            None,
            {"threadIds": StringCollection(thread_ids)},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type
