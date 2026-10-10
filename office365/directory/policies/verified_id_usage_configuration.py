from __future__ import annotations

from dataclasses import dataclass

from office365.directory.identities.providers.verified_id_usage_configuration_purpose import (
    VerifiedIdUsageConfigurationPurpose,
)
from office365.runtime.client_value import ClientValue


@dataclass
class VerifiedIdUsageConfiguration(ClientValue):
    isEnabledForTestOnly: bool | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.VerifiedIdUsageConfiguration"

    purpose: VerifiedIdUsageConfigurationPurpose = VerifiedIdUsageConfigurationPurpose.recovery
