from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.client_result import ClientResult
from office365.runtime.queries.function import FunctionQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext


class PersonalListsProxy(Entity):
    @staticmethod
    def get_personal_lists_proxy(context: ClientContext, sort_by: int, template_type_id: str) -> ClientResult[bytes]:
        """GetPersonalListsProxy operation.

        Args:
            sort_by (int):
                sortBy parameter
            template_type_id (str):
                templateTypeId parameter
        """
        from office365.sharepoint.userprofiles.personallistsproxy import (
            PersonalListsProxy,
        )

        return_type = ClientResult(context, bytes())
        qry = FunctionQuery(
            PersonalListsProxy(context),
            "GetPersonalListsProxy",
            [sort_by, template_type_id],
            return_type,
            return_raw_content=True,
        )
        context.add_query(qry)
        return return_type
