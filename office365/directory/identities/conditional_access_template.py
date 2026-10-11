from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.policies.conditionalaccess.policy_detail import (
        ConditionalAccessPolicyDetail,
    )
    from office365.directory.policies.conditionalaccess.templatescenarios import (
        TemplateScenarios,
    )


class ConditionalAccessTemplate(Entity):
    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def details(self) -> ConditionalAccessPolicyDetail:
        """Gets the details property"""
        from office365.directory.policies.conditionalaccess.policy_detail import (
            ConditionalAccessPolicyDetail,
        )

        return self.properties.get("details", ConditionalAccessPolicyDetail())

    @property
    def name(self) -> Optional[str]:
        """Gets the name property"""
        return self.properties.get("name", None)

    @property
    def scenarios(self) -> TemplateScenarios:
        """Gets the scenarios property"""
        from office365.directory.policies.conditionalaccess.templatescenarios import (
            TemplateScenarios,
        )

        return self.properties.get("scenarios", TemplateScenarios.new)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ConditionalAccessTemplate"
