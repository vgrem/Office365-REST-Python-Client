from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class LocalizedLabel(ClientValue):
    """
    Represents the localized name used in the term store, which identifies the name in the localized language.
    For more information, see localizedLabel.
    """

    name: str | None = None
    languageTag: str = "en-US"
    isDefault: bool = True

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.termStore.LocalizedLabel"
