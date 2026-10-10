from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from office365.directory.synchronization.linked_objects import SynchronizationLinkedObjects


@dataclass
class SynchronizationJobSubject(ClientValue):
    links: SynchronizationLinkedObjects | None = None
    objectId: str | None = None
    objectTypeName: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SynchronizationJobSubject"
