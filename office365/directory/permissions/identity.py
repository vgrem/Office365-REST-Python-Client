from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class Identity(ClientValue):
    """The Identity resource represents an identity of an actor. For example, an actor can be a user, device,
    or application."""

    displayName: str | None = None
    id: str | None = None

    def __str__(self) -> str:
        """Best-effort human-readable label (display name or object id)."""
        return self.displayName or self.id or ""

    def __repr__(self):
        return repr(self.to_json())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Identity"
