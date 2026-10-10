from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext


class UserAITokens(Entity):
    @staticmethod
    def add_ai_tokens(
        context: ClientContext, input_tokens: int, cache_tokens: int, output_tokens: int, model: str
    ) -> ClientResult[bytes]:
        """AddAITokens operation.

        Args:
            input_tokens (int):
                inputTokens parameter
            cache_tokens (int):
                cacheTokens parameter
            output_tokens (int):
                outputTokens parameter
            model (str):
                model parameter
        """
        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            UserAITokens(context),
            "AddAITokens",
            None,
            {"inputTokens": input_tokens, "cacheTokens": cache_tokens, "outputTokens": output_tokens, "model": model},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_ai_tokens(context: ClientContext, model: str) -> ClientResult[bytes]:
        """GetAITokens operation.

        Args:
            model (str):
                model parameter
        """
        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            UserAITokens(context), "GetAITokens", None, {"model": model}, None, return_type, True
        )
        context.add_query(qry)
        return return_type
