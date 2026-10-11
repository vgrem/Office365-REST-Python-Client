from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.security.datasecurity.process_content_request import (
        ProcessContentRequest,
    )


class ContentActivity(Entity):
    @property
    def content_metadata(self) -> ProcessContentRequest:
        """Gets the contentMetadata property"""
        from office365.security.datasecurity.process_content_request import (
            ProcessContentRequest,
        )

        return self.properties.get("contentMetadata", ProcessContentRequest())

    @property
    def scope_identifier(self) -> Optional[str]:
        """Gets the scopeIdentifier property"""
        return self.properties.get("scopeIdentifier", None)

    @property
    def user_id(self) -> Optional[str]:
        """Gets the userId property"""
        return self.properties.get("userId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ContentActivity"
