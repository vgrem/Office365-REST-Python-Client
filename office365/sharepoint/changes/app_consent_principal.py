from __future__ import annotations

from typing import Optional

from office365.sharepoint.changes.change import Change


class ChangeAppConsentPrincipal(Change):
    """"""

    @property
    def app_consent_principal_id(self) -> Optional[int]:
        """Gets the AppConsentPrincipalId property"""
        return self.properties.get("AppConsentPrincipalId", None)
