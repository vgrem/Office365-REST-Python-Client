from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from office365.directory.policies.unifiedrolemanagement.policyruletargetoperations import (
    UnifiedRoleManagementPolicyRuleTargetOperations,
)
from office365.entity_collection import EntityCollection
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.directory.objects.object import DirectoryObject


@dataclass
class UnifiedRoleManagementPolicyRuleTarget(ClientValue):
    caller: str | None = None
    enforcedSettings: StringCollection = field(default_factory=StringCollection)
    inheritableSettings: StringCollection = field(default_factory=StringCollection)
    level: str | None = None
    operations: ClientValueCollection[UnifiedRoleManagementPolicyRuleTargetOperations] = field(
        default_factory=lambda: ClientValueCollection(UnifiedRoleManagementPolicyRuleTargetOperations)
    )
    targetObjects: EntityCollection[DirectoryObject] | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UnifiedRoleManagementPolicyRuleTarget"
