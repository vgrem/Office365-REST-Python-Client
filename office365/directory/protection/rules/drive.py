from __future__ import annotations

from typing import Optional

from office365.directory.protection.rules.base import ProtectionRuleBase


class DriveProtectionRule(ProtectionRuleBase):
    """Represents a protection rule associated with a OneDrive for Business protection policy."""

    @property
    def drive_expression(self) -> Optional[str]:
        """Gets the driveExpression property"""
        return self.properties.get("driveExpression", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DriveProtectionRule"
