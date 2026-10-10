from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext


class RecommendationCollection(Entity):
    @staticmethod
    def dismissed(context: ClientContext, recommendation_id: str) -> ClientResult[str]:
        """Dismissed operation.

        Args:
            recommendation_id (str):
                recommendationId parameter
        """
        from office365.sharepoint.lists.recommendationcollection import (
            RecommendationCollection,
        )

        return_type = ClientResult(context, str())
        qry = ServiceOperationQuery(
            RecommendationCollection(context),
            "Dismissed",
            None,
            {"recommendationId": recommendation_id},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def events(context: ClientContext, event_details: str) -> ClientResult[str]:
        """Events operation.

        Args:
            event_details (str):
                eventDetails parameter
        """
        from office365.sharepoint.lists.recommendationcollection import (
            RecommendationCollection,
        )

        return_type = ClientResult(context, str())
        qry = ServiceOperationQuery(
            RecommendationCollection(context), "Events", None, {"eventDetails": event_details}, None, return_type, True
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_recommendations_as_stream(context: ClientContext, top: int) -> ClientResult[bytes]:
        """GetRecommendationsAsStream operation.

        Args:
            top (int):
                top parameter
        """
        from office365.sharepoint.lists.recommendationcollection import (
            RecommendationCollection,
        )

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            RecommendationCollection(context), "GetRecommendationsAsStream", None, {"top": top}, None, return_type, True
        )
        context.add_query(qry)
        return return_type
