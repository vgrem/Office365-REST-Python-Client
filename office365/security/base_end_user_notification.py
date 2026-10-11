from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from office365.security.end_user_notification import EndUserNotification


@dataclass
class BaseEndUserNotification(ClientValue):
    defaultLanguage: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.BaseEndUserNotification"

    endUserNotification: EndUserNotification | None = None
