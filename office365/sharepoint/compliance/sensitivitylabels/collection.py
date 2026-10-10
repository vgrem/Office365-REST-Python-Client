from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.client_result import ClientResult
from office365.runtime.queries.function import FunctionQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext


class SensitivityLabelCollection(Entity):
    @staticmethod
    def get_sensitivity_labels_as_stream(context: ClientContext, expand: str, filter_: str) -> ClientResult[bytes]:
        """GetSensitivityLabelsAsStream operation.

        Args:
            expand (str):
                expand parameter
            filter_ (str):
                filter parameter
        """
        from office365.sharepoint.compliance.sensitivitylabels.collection import (
            SensitivityLabelCollection,
        )

        return_type = ClientResult(context, bytes())
        qry = FunctionQuery(
            SensitivityLabelCollection(context),
            "GetSensitivityLabelsAsStream",
            [expand, filter_],
            return_type,
            return_raw_content=True,
        )
        context.add_query(qry)
        return return_type
