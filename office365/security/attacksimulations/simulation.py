from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath
from office365.security.attacksimulations.reports.report import (
    SimulationReport,
)

if TYPE_CHECKING:
    from office365.directory.o_auth_consent_app_detail import OAuthConsentAppDetail
    from office365.directory.permissions.email_identity import EmailIdentity
    from office365.security.account_target_content import AccountTargetContent
    from office365.security.attacksimulations.landing_page import LandingPage
    from office365.security.attacksimulations.login_page import LoginPage
    from office365.security.attacksimulations.payload import Payload
    from office365.security.attacksimulations.payloaddeliveryplatform import (
        PayloadDeliveryPlatform,
    )
    from office365.security.attacksimulations.simulationattacktechnique import (
        SimulationAttackTechnique,
    )
    from office365.security.attacksimulations.simulationattacktype import (
        SimulationAttackType,
    )
    from office365.security.attacksimulations.simulationstatus import (
        SimulationStatus,
    )
    from office365.security.end_user_notification_setting import (
        EndUserNotificationSetting,
    )
    from office365.security.training_setting import TrainingSetting


class Simulation(Entity):
    """
    Represents an attack simulation training campaign in a tenant.

    Attack simulation and training is a service available as part of Microsoft Defender for Office 365.
    This service lets tenant users experience a realistic benign phishing attack and learn from it.
    The service enables tenant administrators to simulate, assign trainings, and read derived insights into online
    behaviors of users in the phishing simulations. The service provides attack simulation reports that help tenants
    identify security knowledge gaps, so that they can further train their users to decrease their susceptibility
    to attacks.

    The attack simulation and training API enables tenant administrators to list launched simulation exercises
    and trainings, and get reports on derived insights into online behaviors of users in the phishing simulations.
    """

    @property
    def report(self):
        """Report of the attack simulation and training campaign."""
        return self.properties.get("report", SimulationReport())

    @property
    def attack_technique(self) -> SimulationAttackTechnique:
        """Gets the attackTechnique property"""
        from office365.security.attacksimulations.simulationattacktechnique import (
            SimulationAttackTechnique,
        )

        return self.properties.get("attackTechnique", SimulationAttackTechnique.unknown)

    @property
    def attack_type(self) -> SimulationAttackType:
        """Gets the attackType property"""
        from office365.security.attacksimulations.simulationattacktype import (
            SimulationAttackType,
        )

        return self.properties.get("attackType", SimulationAttackType.unknown)

    @property
    def automation_id(self) -> Optional[str]:
        """Gets the automationId property"""
        return self.properties.get("automationId", None)

    @property
    def completion_date_time(self) -> Optional[datetime]:
        """Gets the completionDateTime property"""
        return self.properties.get("completionDateTime", datetime.min)

    @property
    def created_by(self) -> EmailIdentity:
        """Gets the createdBy property"""
        from office365.directory.permissions.email_identity import EmailIdentity

        return self.properties.get("createdBy", EmailIdentity())

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def duration_in_days(self) -> Optional[int]:
        """Gets the durationInDays property"""
        return self.properties.get("durationInDays", None)

    @property
    def end_user_notification_setting(self) -> EndUserNotificationSetting:
        """Gets the endUserNotificationSetting property"""
        from office365.security.end_user_notification_setting import (
            EndUserNotificationSetting,
        )

        return self.properties.get("endUserNotificationSetting", EndUserNotificationSetting())

    @property
    def excluded_account_target(self) -> AccountTargetContent:
        """Gets the excludedAccountTarget property"""
        from office365.security.account_target_content import (
            AccountTargetContent,
        )

        return self.properties.get("excludedAccountTarget", AccountTargetContent())

    @property
    def included_account_target(self) -> AccountTargetContent:
        """Gets the includedAccountTarget property"""
        from office365.security.account_target_content import (
            AccountTargetContent,
        )

        return self.properties.get("includedAccountTarget", AccountTargetContent())

    @property
    def is_automated(self) -> Optional[bool]:
        """Gets the isAutomated property"""
        return self.properties.get("isAutomated", None)

    @property
    def last_modified_by(self) -> EmailIdentity:
        """Gets the lastModifiedBy property"""
        from office365.directory.permissions.email_identity import EmailIdentity

        return self.properties.get("lastModifiedBy", EmailIdentity())

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def launch_date_time(self) -> Optional[datetime]:
        """Gets the launchDateTime property"""
        return self.properties.get("launchDateTime", datetime.min)

    @property
    def oauth_consent_app_detail(self) -> OAuthConsentAppDetail:
        """Gets the oAuthConsentAppDetail property"""
        from office365.directory.o_auth_consent_app_detail import OAuthConsentAppDetail

        return self.properties.get("oAuthConsentAppDetail", OAuthConsentAppDetail())

    @property
    def payload_delivery_platform(self) -> PayloadDeliveryPlatform:
        """Gets the payloadDeliveryPlatform property"""
        from office365.security.attacksimulations.payloaddeliveryplatform import (
            PayloadDeliveryPlatform,
        )

        return self.properties.get("payloadDeliveryPlatform", PayloadDeliveryPlatform.unknown)

    @property
    def status(self) -> SimulationStatus:
        """Gets the status property"""
        from office365.security.attacksimulations.simulationstatus import (
            SimulationStatus,
        )

        return self.properties.get("status", SimulationStatus.unknown)

    @property
    def training_setting(self) -> TrainingSetting:
        """Gets the trainingSetting property"""
        from office365.security.training_setting import TrainingSetting

        return self.properties.get("trainingSetting", TrainingSetting())

    @property
    def landing_page(self) -> LandingPage:
        """Gets the landingPage property"""
        from office365.security.attacksimulations.landing_page import (
            LandingPage,
        )

        return self.properties.get(
            "landingPage", LandingPage(self.context, ResourcePath("landingPage", self.resource_path))
        )

    @property
    def login_page(self) -> LoginPage:
        """Gets the loginPage property"""
        from office365.security.attacksimulations.login_page import LoginPage

        return self.properties.get("loginPage", LoginPage(self.context, ResourcePath("loginPage", self.resource_path)))

    @property
    def payload(self) -> Payload:
        """Gets the payload property"""
        from office365.security.attacksimulations.payload import Payload

        return self.properties.get("payload", Payload(self.context, ResourcePath("payload", self.resource_path)))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Simulation"
