from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from office365.directory.identities.providers.verified_id_usage_configuration_purpose import (
        VerifiedIdUsageConfigurationPurpose,
    )


@dataclass
class VerifiedIdUsageConfiguration(ClientValue):
    isEnabledForTestOnly: bool | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.VerifiedIdUsageConfiguration"

    purpose: VerifiedIdUsageConfigurationPurpose = VerifiedIdUsageConfigurationPurpose.recovery
