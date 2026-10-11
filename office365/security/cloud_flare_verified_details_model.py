from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.security.cloud_flare_rule_model import CloudFlareRuleModel
from office365.security.cloud_flare_ruleset_model import (
    CloudFlareRulesetModel,
)


@dataclass
class CloudFlareVerifiedDetailsModel(ClientValue):
    enabledCustomRules: ClientValueCollection[CloudFlareRuleModel] = field(
        default_factory=lambda: ClientValueCollection(CloudFlareRuleModel)
    )
    enabledRecommendedRulesets: ClientValueCollection[CloudFlareRulesetModel] = field(
        default_factory=lambda: ClientValueCollection(CloudFlareRulesetModel)
    )
    zoneId: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CloudFlareVerifiedDetailsModel"
