from __future__ import annotations

from datetime import time
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.configurations.sharedpc.allowedaccounttype import (
        SharedPCAllowedAccountType,
    )
    from office365.intune.devices.configurations.windows.shared_pc_account_manager_policy import (
        SharedPCAccountManagerPolicy,
    )


class SharedPCConfiguration(Entity):
    @property
    def account_manager_policy(self) -> SharedPCAccountManagerPolicy:
        """Gets the accountManagerPolicy property"""
        from office365.intune.devices.configurations.windows.shared_pc_account_manager_policy import (
            SharedPCAccountManagerPolicy,
        )

        return self.properties.get("accountManagerPolicy", SharedPCAccountManagerPolicy())

    @property
    def allowed_accounts(self) -> SharedPCAllowedAccountType:
        """Gets the allowedAccounts property"""
        from office365.intune.devices.configurations.sharedpc.allowedaccounttype import (
            SharedPCAllowedAccountType,
        )

        return self.properties.get("allowedAccounts", SharedPCAllowedAccountType.guest)

    @property
    def allow_local_storage(self) -> Optional[bool]:
        """Gets the allowLocalStorage property"""
        return self.properties.get("allowLocalStorage", None)

    @property
    def disable_account_manager(self) -> Optional[bool]:
        """Gets the disableAccountManager property"""
        return self.properties.get("disableAccountManager", None)

    @property
    def disable_edu_policies(self) -> Optional[bool]:
        """Gets the disableEduPolicies property"""
        return self.properties.get("disableEduPolicies", None)

    @property
    def disable_power_policies(self) -> Optional[bool]:
        """Gets the disablePowerPolicies property"""
        return self.properties.get("disablePowerPolicies", None)

    @property
    def disable_sign_in_on_resume(self) -> Optional[bool]:
        """Gets the disableSignInOnResume property"""
        return self.properties.get("disableSignInOnResume", None)

    @property
    def enabled(self) -> Optional[bool]:
        """Gets the enabled property"""
        return self.properties.get("enabled", None)

    @property
    def idle_time_before_sleep_in_seconds(self) -> Optional[int]:
        """Gets the idleTimeBeforeSleepInSeconds property"""
        return self.properties.get("idleTimeBeforeSleepInSeconds", None)

    @property
    def kiosk_app_display_name(self) -> Optional[str]:
        """Gets the kioskAppDisplayName property"""
        return self.properties.get("kioskAppDisplayName", None)

    @property
    def kiosk_app_user_model_id(self) -> Optional[str]:
        """Gets the kioskAppUserModelId property"""
        return self.properties.get("kioskAppUserModelId", None)

    @property
    def maintenance_start_time(self) -> Optional[time]:
        """Gets the maintenanceStartTime property"""
        return self.properties.get("maintenanceStartTime", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SharedPCConfiguration"
