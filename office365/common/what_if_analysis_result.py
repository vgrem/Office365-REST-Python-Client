from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.policies.conditionalaccess.whatifanalysisreasons import (
        WhatIfAnalysisReasons,
    )


class WhatIfAnalysisResult(Entity):
    @property
    def analysis_reasons(self) -> WhatIfAnalysisReasons:
        """Gets the analysisReasons property"""
        from office365.directory.policies.conditionalaccess.whatifanalysisreasons import (
            WhatIfAnalysisReasons,
        )

        return self.properties.get("analysisReasons", WhatIfAnalysisReasons.notSet)

    @property
    def policy_applies(self) -> Optional[bool]:
        """Gets the policyApplies property"""
        return self.properties.get("policyApplies", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WhatIfAnalysisResult"
