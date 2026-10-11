from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class CloudFlareRulesetModel(ClientValue):
    name: str | None = None
    phaseName: str | None = None
    rulesetId: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CloudFlareRulesetModel"
