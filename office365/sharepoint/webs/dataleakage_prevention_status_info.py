from __future__ import annotations

from typing import Optional

from office365.sharepoint.entity import Entity


class SPDataLeakagePreventionStatusInfo(Entity):
    """"""

    @property
    def contains_confidential_info(self) -> Optional[bool]:
        """Gets the ContainsConfidentialInfo property"""
        return self.properties.get("ContainsConfidentialInfo", None)

    @property
    def contains_confidential_info_learn_more_url(self) -> Optional[str]:
        """Gets the ContainsConfidentialInfoLearnMoreUrl property"""
        return self.properties.get("ContainsConfidentialInfoLearnMoreUrl", None)

    @property
    def external_sharing_tips_enabled(self) -> Optional[bool]:
        """Gets the ExternalSharingTipsEnabled property"""
        return self.properties.get("ExternalSharingTipsEnabled", None)

    @property
    def external_sharing_tips_learn_more_url(self) -> Optional[str]:
        """Gets the ExternalSharingTipsLearnMoreUrl property"""
        return self.properties.get("ExternalSharingTipsLearnMoreUrl", None)
