from __future__ import annotations

from dataclasses import dataclass

from office365.directory.identitygovernance.accessreview.principal_scope_type import (
    AccessReviewPrincipalScopeType,
)
from office365.runtime.client_value import ClientValue


@dataclass
class AccessReviewPrincipalScope(ClientValue):
    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AccessReviewPrincipalScope"

    scopeType: AccessReviewPrincipalScopeType = AccessReviewPrincipalScopeType.allUsers
