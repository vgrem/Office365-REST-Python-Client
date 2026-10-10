from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.dynamiccontent.add_raw_questions_payload import (
        AddRawQuestionsPayload,
    )
    from office365.sharepoint.dynamiccontent.aggregated_questions_payload import (
        AggregatedQuestionsPayload,
    )
    from office365.sharepoint.dynamiccontent.aggregated_questions_result import (
        AggregatedQuestionsResult,
    )
    from office365.sharepoint.dynamiccontent.delete_aggregated_questions_payload import (
        DeleteAggregatedQuestionsPayload,
    )
    from office365.sharepoint.dynamiccontent.ensure_list_item_result import (
        EnsureListItemResult,
    )
    from office365.sharepoint.dynamiccontent.faq_request_payload import (
        FAQRequestPayload,
    )
    from office365.sharepoint.dynamiccontent.faq_suggestion_item import (
        FaqSuggestionItem,
    )
    from office365.sharepoint.dynamiccontent.raw_questions_result import (
        RawQuestionsResult,
    )
    from office365.sharepoint.dynamiccontent.source_file_rquest import SourceFileRquest
    from office365.sharepoint.dynamiccontent.suggestion_item_parameters import (
        SuggestionItemParameters,
    )


class DynamicContentUpdateService(Entity):
    def add_faq_user_submitted_questions(self, data: AddRawQuestionsPayload) -> Self:
        """AddFAQUserSubmittedQuestions operation.

        Args:
            data (AddRawQuestionsPayload):
                data parameter
        """
        qry = ServiceOperationQuery(self, "AddFAQUserSubmittedQuestions", None, {"data": data}, None, None)
        self.context.add_query(qry)
        return self

    def add_or_update_faq_content_update_suggestion(self, suggestion: SuggestionItemParameters) -> Self:
        """AddOrUpdateFAQContentUpdateSuggestion operation.

        Args:
            suggestion (SuggestionItemParameters):
                suggestion parameter
        """
        qry = ServiceOperationQuery(
            self, "AddOrUpdateFAQContentUpdateSuggestion", None, {"suggestion": suggestion}, None, None
        )
        self.context.add_query(qry)
        return self

    def delete_faq_aggregated_question(self, data: DeleteAggregatedQuestionsPayload) -> Self:
        """DeleteFAQAggregatedQuestion operation.

        Args:
            data (DeleteAggregatedQuestionsPayload):
                data parameter
        """
        qry = ServiceOperationQuery(self, "DeleteFAQAggregatedQuestion", None, {"data": data}, None, None)
        self.context.add_query(qry)
        return self

    def delete_faq_content_update_suggestion(self, suggestion: SuggestionItemParameters) -> Self:
        """DeleteFAQContentUpdateSuggestion operation.

        Args:
            suggestion (SuggestionItemParameters):
                suggestion parameter
        """
        qry = ServiceOperationQuery(
            self, "DeleteFAQContentUpdateSuggestion", None, {"suggestion": suggestion}, None, None
        )
        self.context.add_query(qry)
        return self

    def ensure_dynamic_content_update_list_feature(self) -> Self:
        """EnsureDynamicContentUpdateListFeature operation."""
        qry = ServiceOperationQuery(self, "EnsureDynamicContentUpdateListFeature", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def ensure_faq_aggregated_questions_list_item(self, data: FAQRequestPayload) -> ClientResult[EnsureListItemResult]:
        """EnsureFAQAggregatedQuestionsListItem operation.

        Args:
            data (FAQRequestPayload):
                data parameter
        """
        from office365.sharepoint.dynamiccontent.ensure_list_item_result import (
            EnsureListItemResult,
        )

        return_type = ClientResult(self.context, EnsureListItemResult())
        qry = ServiceOperationQuery(
            self, "EnsureFAQAggregatedQuestionsListItem", None, {"data": data}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def ensure_file_change_detect_work_item(self, request: SourceFileRquest) -> ClientResult[bool]:
        """EnsureFileChangeDetectWorkItem operation.

        Args:
            request (SourceFileRquest):
                request parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(
            self, "EnsureFileChangeDetectWorkItem", None, {"request": request}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def faq_aggregated_questions(
        self, page_list_item_id: int, web_part_instance_id: UUID, unique_id: UUID
    ) -> ClientResult[AggregatedQuestionsResult]:
        """FAQAggregatedQuestions operation.

        Args:
            page_list_item_id (int):
                pageListItemId parameter
            web_part_instance_id (UUID):
                webPartInstanceId parameter
            unique_id (UUID):
                uniqueId parameter
        """
        from office365.sharepoint.dynamiccontent.aggregated_questions_result import (
            AggregatedQuestionsResult,
        )

        return_type = ClientResult(self.context, AggregatedQuestionsResult())
        qry = FunctionQuery(
            self, "FAQAggregatedQuestions", [page_list_item_id, web_part_instance_id, unique_id], return_type
        )
        self.context.add_query(qry)
        return return_type

    def faq_content_update_suggestions(
        self, max_item_count: int, snoozed_identifiers: str
    ) -> ClientResult[ClientValueCollection[FaqSuggestionItem]]:
        """FAQContentUpdateSuggestions operation.

        Args:
            max_item_count (int):
                maxItemCount parameter
            snoozed_identifiers (str):
                snoozedIdentifiers parameter
        """
        from office365.sharepoint.dynamiccontent.faq_suggestion_item import (
            FaqSuggestionItem,
        )

        return_type = ClientResult(self.context, ClientValueCollection[FaqSuggestionItem]())
        qry = FunctionQuery(self, "FAQContentUpdateSuggestions", [max_item_count, snoozed_identifiers], return_type)
        self.context.add_query(qry)
        return return_type

    def faq_user_submitted_questions(
        self, page_list_item_id: int, web_part_instance_id: UUID, unique_id: UUID
    ) -> ClientResult[RawQuestionsResult]:
        """FAQUserSubmittedQuestions operation.

        Args:
            page_list_item_id (int):
                pageListItemId parameter
            web_part_instance_id (UUID):
                webPartInstanceId parameter
            unique_id (UUID):
                uniqueId parameter
        """
        from office365.sharepoint.dynamiccontent.raw_questions_result import (
            RawQuestionsResult,
        )

        return_type = ClientResult(self.context, RawQuestionsResult())
        qry = FunctionQuery(
            self, "FAQUserSubmittedQuestions", [page_list_item_id, web_part_instance_id, unique_id], return_type
        )
        self.context.add_query(qry)
        return return_type

    def update_faq_aggregated_questions(self, aggregated_data: AggregatedQuestionsPayload) -> Self:
        """UpdateFAQAggregatedQuestions operation.

        Args:
            aggregated_data (AggregatedQuestionsPayload):
                aggregatedData parameter
        """
        qry = ServiceOperationQuery(
            self, "UpdateFAQAggregatedQuestions", None, {"aggregatedData": aggregated_data}, None, None
        )
        self.context.add_query(qry)
        return self
