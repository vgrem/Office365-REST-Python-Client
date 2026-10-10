from __future__ import annotations

from typing import Optional

from office365.sharepoint.entity import Entity


class SPMachineLearningEnabled(Entity):
    """ """

    @property
    def is_syntex_payg_enabled(self) -> Optional[bool]:
        """ """
        return self.properties.get("IsSyntexPAYGEnabled", None)

    @property
    def entity_type_name(self):
        return "Microsoft.Office.Server.ContentCenter.SPMachineLearningEnabled"

    @property
    def is_copilot_license_enabled(self) -> Optional[bool]:
        """Gets the IsCopilotLicenseEnabled property"""
        return self.properties.get("IsCopilotLicenseEnabled", None)

    @property
    def machine_learning_capture_enabled(self) -> Optional[bool]:
        """Gets the MachineLearningCaptureEnabled property"""
        return self.properties.get("MachineLearningCaptureEnabled", None)

    @property
    def machine_learning_experience_enabled(self) -> Optional[bool]:
        """Gets the MachineLearningExperienceEnabled property"""
        return self.properties.get("MachineLearningExperienceEnabled", None)

    @property
    def tenant_syntex_enabled(self) -> Optional[bool]:
        """Gets the TenantSyntexEnabled property"""
        return self.properties.get("TenantSyntexEnabled", None)

    @property
    def tenant_syntex_v2_enabled(self) -> Optional[bool]:
        """Gets the TenantSyntexV2Enabled property"""
        return self.properties.get("TenantSyntexV2Enabled", None)

    @property
    def user_syntex_enabled(self) -> Optional[bool]:
        """Gets the UserSyntexEnabled property"""
        return self.properties.get("UserSyntexEnabled", None)

    @property
    def user_syntex_v2_enabled(self) -> Optional[bool]:
        """Gets the UserSyntexV2Enabled property"""
        return self.properties.get("UserSyntexV2Enabled", None)
