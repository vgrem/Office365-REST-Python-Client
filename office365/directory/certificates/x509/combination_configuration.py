from __future__ import annotations

from office365.entity import Entity
from office365.runtime.types.collections import StringCollection


class X509CertificateCombinationConfiguration(Entity):
    @property
    def allowed_issuer_skis(self) -> StringCollection:
        """Gets the allowedIssuerSkis property"""
        return self.properties.get("allowedIssuerSkis", StringCollection())

    @property
    def allowed_policy_oids(self) -> StringCollection:
        """Gets the allowedPolicyOIDs property"""
        return self.properties.get("allowedPolicyOIDs", StringCollection())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.X509CertificateCombinationConfiguration"
