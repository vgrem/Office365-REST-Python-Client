from __future__ import annotations

from typing import Optional

from office365.directory.protection.rules.base import ProtectionRuleBase


class SiteProtectionRule(ProtectionRuleBase):
    @property
    def site_expression(self) -> Optional[str]:
        """Gets the siteExpression property"""
        return self.properties.get("siteExpression", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SiteProtectionRule"
