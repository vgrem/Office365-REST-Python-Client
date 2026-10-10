from __future__ import annotations

from enum import Enum


class AccessReviewResourceScopeType(Enum):
    group = "0"
    catalog = "1"
    servicePrincipal = "2"
    directoryRole = "3"
    accessPackageAssignmentPolicy = "4"
    unknownFutureValue = "5"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AccessReviewResourceScopeType"
