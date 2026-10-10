from __future__ import annotations

import json
from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class LocalizedName(ClientValue):
    """
    Represents the localized name used in the term store, which identifies the name in the localized language.
    For more information, see localizedLabel.
    """

    name: str | None = None
    languageTag: str = "en-US"

    def __repr__(self):
        return json.dumps(self.to_json())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.termStore.LocalizedName"
