from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.microfeed.posts.definition import MicrofeedPostDefinition


class MicrofeedPostDefinitionManager(Entity):
    @property
    def entity_type_name(self) -> str:
        return "SP.Microfeed.MicrofeedPostDefinitionManager"

    def delete_microfeed_post_definition(self, post_definition: MicrofeedPostDefinition) -> ClientResult[bool]:
        """DeleteMicrofeedPostDefinition operation.

        Args:
            post_definition (MicrofeedPostDefinition):
                postDefinition parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(
            self, "DeleteMicrofeedPostDefinition", None, {"postDefinition": post_definition}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_microfeed_post_definition(self, definition_name: str) -> ClientResult[MicrofeedPostDefinition]:
        """GetMicrofeedPostDefinition operation.

        Args:
            definition_name (str):
                definitionName parameter
        """
        from office365.sharepoint.microfeed.posts.definition import (
            MicrofeedPostDefinition,
        )

        return_type = ClientResult(self.context, MicrofeedPostDefinition())
        qry = ServiceOperationQuery(
            self, "GetMicrofeedPostDefinition", None, {"definitionName": definition_name}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_microfeed_post_definitions(self) -> ClientResult[ClientValueCollection[MicrofeedPostDefinition]]:
        """GetMicrofeedPostDefinitions operation."""
        from office365.sharepoint.microfeed.posts.definition import (
            MicrofeedPostDefinition,
        )

        return_type = ClientResult(self.context, ClientValueCollection[MicrofeedPostDefinition]())
        qry = ServiceOperationQuery(self, "GetMicrofeedPostDefinitions", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def new_microfeed_post_definition(self, definition_name: str) -> ClientResult[MicrofeedPostDefinition]:
        """NewMicrofeedPostDefinition operation.

        Args:
            definition_name (str):
                definitionName parameter
        """
        from office365.sharepoint.microfeed.posts.definition import (
            MicrofeedPostDefinition,
        )

        return_type = ClientResult(self.context, MicrofeedPostDefinition())
        qry = ServiceOperationQuery(
            self, "NewMicrofeedPostDefinition", None, {"definitionName": definition_name}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def update_microfeed_post_definition(
        self, post_definition: MicrofeedPostDefinition
    ) -> ClientResult[MicrofeedPostDefinition]:
        """UpdateMicrofeedPostDefinition operation.

        Args:
            post_definition (MicrofeedPostDefinition):
                postDefinition parameter
        """
        from office365.sharepoint.microfeed.posts.definition import (
            MicrofeedPostDefinition,
        )

        return_type = ClientResult(self.context, MicrofeedPostDefinition())
        qry = ServiceOperationQuery(
            self, "UpdateMicrofeedPostDefinition", None, {"postDefinition": post_definition}, None, return_type
        )
        self.context.add_query(qry)
        return return_type
