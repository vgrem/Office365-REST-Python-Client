from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from office365.common.intune_brand import IntuneBrand
from office365.directory.rolemanagement.roles.permission import RolePermission
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.intune.audit.event_collection import AuditEventCollection
from office365.intune.devices.category import DeviceCategory
from office365.intune.devices.enrollment.configuration import (
    DeviceEnrollmentConfiguration,
)
from office365.intune.devices.management.managed.collection import (
    ManagedDeviceCollection,
)
from office365.intune.devices.management.reports.reports import DeviceManagementReports
from office365.intune.devices.management.terms_and_conditions import TermsAndConditions
from office365.intune.devices.management.virtualendpoint.virtual_endpoint import (
    VirtualEndpoint,
)
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.common.role_definition import RoleDefinition
    from office365.intune.devices.and_app_management_role_assignment import (
        DeviceAndAppManagementRoleAssignment,
    )
    from office365.intune.devices.compliance.management_partner import (
        ComplianceManagementPartner,
    )
    from office365.intune.devices.compliance.policy import DeviceCompliancePolicy
    from office365.intune.devices.compliance_policy_device_state_summary import (
        DeviceCompliancePolicyDeviceStateSummary,
    )
    from office365.intune.devices.compliance_policy_setting_state_summary import (
        DeviceCompliancePolicySettingStateSummary,
    )
    from office365.intune.devices.configuration_device_state_summary import (
        DeviceConfigurationDeviceStateSummary,
    )
    from office365.intune.devices.configurations.configuration import (
        DeviceConfiguration,
    )
    from office365.intune.devices.management.apple_push_notification_certificate import (
        ApplePushNotificationCertificate,
    )
    from office365.intune.devices.management.detected_app import DetectedApp
    from office365.intune.devices.management.device_protection_overview import (
        DeviceProtectionOverview,
    )
    from office365.intune.devices.management.imported_windows_autopilot_device_identity import (
        ImportedWindowsAutopilotDeviceIdentity,
    )
    from office365.intune.devices.management.ios_update_device_status import IosUpdateDeviceStatus
    from office365.intune.devices.management.managed.device_overview import ManagedDeviceOverview
    from office365.intune.devices.management.mobile_threat_defense_connector import (
        MobileThreatDefenseConnector,
    )
    from office365.intune.devices.management.mobileapps.mobile_app_troubleshooting_event import (
        MobileAppTroubleshootingEvent,
    )
    from office365.intune.devices.management.notification_message_template import (
        NotificationMessageTemplate,
    )
    from office365.intune.devices.management.on_premises_conditional_access_settings import (
        OnPremisesConditionalAccessSettings,
    )
    from office365.intune.devices.management.remoteassistance.partner import (
        RemoteAssistancePartner,
    )
    from office365.intune.devices.management.resource_operation import ResourceOperation
    from office365.intune.devices.management.settings import DeviceManagementSettings
    from office365.intune.devices.management.software_update_status_summary import (
        SoftwareUpdateStatusSummary,
    )
    from office365.intune.devices.management.subscriptionstate import (
        DeviceManagementSubscriptionState,
    )
    from office365.intune.devices.management.user_experience_analytics_settings import (
        UserExperienceAnalyticsSettings,
    )
    from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_app_health_app_performance_by_app_version_details import (  # noqa: E501
        UserExperienceAnalyticsAppHealthAppPerformanceByAppVersionDetails,
    )
    from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_app_health_app_performance_by_app_version_device_id import (  # noqa: E501
        UserExperienceAnalyticsAppHealthAppPerformanceByAppVersionDeviceId,
    )
    from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_app_health_app_performance_by_os_version import (  # noqa: E501
        UserExperienceAnalyticsAppHealthAppPerformanceByOSVersion,
    )
    from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_app_health_application_performance import (  # noqa: E501
        UserExperienceAnalyticsAppHealthApplicationPerformance,
    )
    from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_app_health_device_model_performance import (  # noqa: E501
        UserExperienceAnalyticsAppHealthDeviceModelPerformance,
    )
    from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_app_health_device_performance import (  # noqa: E501
        UserExperienceAnalyticsAppHealthDevicePerformance,
    )
    from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_app_health_device_performance_details import (  # noqa: E501
        UserExperienceAnalyticsAppHealthDevicePerformanceDetails,
    )
    from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_app_health_os_version_performance import (  # noqa: E501
        UserExperienceAnalyticsAppHealthOSVersionPerformance,
    )
    from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_baseline import (
        UserExperienceAnalyticsBaseline,
    )
    from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_category import (
        UserExperienceAnalyticsCategory,
    )
    from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_device_performance import (  # noqa: E501
        UserExperienceAnalyticsDevicePerformance,
    )
    from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_device_scores import (
        UserExperienceAnalyticsDeviceScores,
    )
    from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_device_startup_history import (  # noqa: E501
        UserExperienceAnalyticsDeviceStartupHistory,
    )
    from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_device_startup_process import (  # noqa: E501
        UserExperienceAnalyticsDeviceStartupProcess,
    )
    from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_device_startup_process_performance import (  # noqa: E501
        UserExperienceAnalyticsDeviceStartupProcessPerformance,
    )
    from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_metric_history import (
        UserExperienceAnalyticsMetricHistory,
    )
    from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_model_scores import (
        UserExperienceAnalyticsModelScores,
    )
    from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_overview import (
        UserExperienceAnalyticsOverview,
    )
    from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_score_history import (
        UserExperienceAnalyticsScoreHistory,
    )
    from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_work_from_anywhere_hardware_readiness_metric import (  # noqa: E501
        UserExperienceAnalyticsWorkFromAnywhereHardwareReadinessMetric,
    )
    from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_work_from_anywhere_metric import (  # noqa: E501
        UserExperienceAnalyticsWorkFromAnywhereMetric,
    )
    from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_work_from_anywhere_model_performance import (  # noqa: E501
        UserExperienceAnalyticsWorkFromAnywhereModelPerformance,
    )
    from office365.intune.devices.management.windows_autopilot_device_identity import (
        WindowsAutopilotDeviceIdentity,
    )
    from office365.intune.devices.management.windows_information_protection_app_learning_summary import (
        WindowsInformationProtectionAppLearningSummary,
    )
    from office365.intune.devices.management.windows_information_protection_network_learning_summary import (
        WindowsInformationProtectionNetworkLearningSummary,
    )
    from office365.intune.devices.management.windows_malware_overview import (
        WindowsMalwareOverview,
    )
    from office365.intune.devices.management.windowsmalware.windows_malware_information import WindowsMalwareInformation
    from office365.intune.devices.management_exchange_connector import (
        DeviceManagementExchangeConnector,
    )
    from office365.intune.devices.management_partner import DeviceManagementPartner
    from office365.intune.devices.management_troubleshooting_event import (
        DeviceManagementTroubleshootingEvent,
    )


class DeviceManagement(Entity):
    """
    The deviceManagement resource represents a tenant's collection device identities that have been pre-staged in
    Intune, and the enrollment profiles that may be assigned to device identities that support pre-enrollment
    configuration.
    """

    def get_effective_permissions(self, scope=None) -> ClientResult[ClientValueCollection[RolePermission]]:
        """Retrieves the effective permissions of the currently authenticated user"""
        return_type = ClientResult(self.context, ClientValueCollection(RolePermission))
        # params = {"scope": scope}
        qry = FunctionQuery(self, "getEffectivePermissions", None, return_type)
        self.context.add_query(qry)
        return return_type

    @odata(name="auditEvents")
    @property
    def audit_events(self) -> AuditEventCollection:
        """"""
        return self.properties.get(
            "auditEvents",
            AuditEventCollection(self.context, ResourcePath("auditEvents", self.resource_path)),
        )

    @odata(name="virtualEndpoint")
    @property
    def virtual_endpoint(self) -> VirtualEndpoint:
        """"""
        return self.properties.get(
            "virtualEndpoint",
            VirtualEndpoint(self.context, ResourcePath("virtualEndpoint", self.resource_path)),
        )

    @odata(name="termsAndConditions")
    @property
    def terms_and_conditions(self) -> EntityCollection[TermsAndConditions]:
        """"""
        return self.properties.get(
            "termsAndConditions",
            EntityCollection(
                self.context,
                TermsAndConditions,
                ResourcePath("termsAndConditions", self.resource_path),
            ),
        )

    @odata(name="deviceCategories")
    @property
    def device_categories(self) -> EntityCollection[DeviceCategory]:
        """"""
        return self.properties.get(
            "deviceCategories",
            EntityCollection(
                self.context,
                DeviceCategory,
                ResourcePath("deviceCategories", self.resource_path),
            ),
        )

    @odata(name="deviceEnrollmentConfigurations")
    @property
    def device_enrollment_configurations(self) -> EntityCollection[DeviceEnrollmentConfiguration]:
        """"""
        return self.properties.get(
            "deviceEnrollmentConfigurations",
            EntityCollection(
                self.context,
                DeviceEnrollmentConfiguration,
                ResourcePath("deviceEnrollmentConfigurations", self.resource_path),
            ),
        )

    @odata(name="intuneBrand")
    @property
    def intune_brand(self) -> IntuneBrand:
        return self.properties.get("intuneBrand", IntuneBrand())

    @odata(name="managedDevices")
    @property
    def managed_devices(self) -> ManagedDeviceCollection:
        """"""
        return self.properties.get(
            "managedDevices",
            ManagedDeviceCollection(
                self.context,
                ResourcePath("managedDevices", self.resource_path),
            ),
        )

    @property
    def reports(self) -> DeviceManagementReports:
        """"""
        return self.properties.get(
            "reports",
            DeviceManagementReports(self.context, ResourcePath("reports", self.resource_path)),
        )

    @property
    def intune_account_id(self) -> Optional[UUID]:
        """Gets the intuneAccountId property"""
        return self.properties.get("intuneAccountId", None)

    @property
    def settings(self) -> DeviceManagementSettings:
        """Gets the settings property"""
        from office365.intune.devices.management.settings import (
            DeviceManagementSettings,
        )

        return self.properties.get("settings", DeviceManagementSettings())

    @property
    def device_protection_overview(self) -> DeviceProtectionOverview:
        """Gets the deviceProtectionOverview property"""
        from office365.intune.devices.management.device_protection_overview import (
            DeviceProtectionOverview,
        )

        return self.properties.get("deviceProtectionOverview", DeviceProtectionOverview())

    @property
    def subscription_state(self) -> DeviceManagementSubscriptionState:
        """Gets the subscriptionState property"""
        from office365.intune.devices.management.subscriptionstate import (
            DeviceManagementSubscriptionState,
        )

        return self.properties.get("subscriptionState", DeviceManagementSubscriptionState.pending)

    @property
    def user_experience_analytics_settings(self) -> UserExperienceAnalyticsSettings:
        """Gets the userExperienceAnalyticsSettings property"""
        from office365.intune.devices.management.user_experience_analytics_settings import (
            UserExperienceAnalyticsSettings,
        )

        return self.properties.get("userExperienceAnalyticsSettings", UserExperienceAnalyticsSettings())

    @property
    def windows_malware_overview(self) -> WindowsMalwareOverview:
        """Gets the windowsMalwareOverview property"""
        from office365.intune.devices.management.windows_malware_overview import (
            WindowsMalwareOverview,
        )

        return self.properties.get("windowsMalwareOverview", WindowsMalwareOverview())

    @property
    def device_compliance_policies(self) -> EntityCollection[DeviceCompliancePolicy]:
        """Gets the deviceCompliancePolicies property"""
        from office365.intune.devices.compliance.policy import DeviceCompliancePolicy

        return self.properties.get(
            "deviceCompliancePolicies",
            EntityCollection[DeviceCompliancePolicy](
                self.context, DeviceCompliancePolicy, ResourcePath("deviceCompliancePolicies", self.resource_path)
            ),
        )

    @property
    def device_compliance_policy_device_state_summary(self) -> DeviceCompliancePolicyDeviceStateSummary:
        """Gets the deviceCompliancePolicyDeviceStateSummary property"""
        from office365.intune.devices.compliance_policy_device_state_summary import (
            DeviceCompliancePolicyDeviceStateSummary,
        )

        return self.properties.get(
            "deviceCompliancePolicyDeviceStateSummary",
            DeviceCompliancePolicyDeviceStateSummary(
                self.context, ResourcePath("deviceCompliancePolicyDeviceStateSummary", self.resource_path)
            ),
        )

    @property
    def device_compliance_policy_setting_state_summaries(
        self,
    ) -> EntityCollection[DeviceCompliancePolicySettingStateSummary]:
        """Gets the deviceCompliancePolicySettingStateSummaries property"""
        from office365.intune.devices.compliance_policy_setting_state_summary import (
            DeviceCompliancePolicySettingStateSummary,
        )

        return self.properties.get(
            "deviceCompliancePolicySettingStateSummaries",
            EntityCollection[DeviceCompliancePolicySettingStateSummary](
                self.context,
                DeviceCompliancePolicySettingStateSummary,
                ResourcePath("deviceCompliancePolicySettingStateSummaries", self.resource_path),
            ),
        )

    @property
    def device_configuration_device_state_summaries(self) -> DeviceConfigurationDeviceStateSummary:
        """Gets the deviceConfigurationDeviceStateSummaries property"""
        from office365.intune.devices.configuration_device_state_summary import (
            DeviceConfigurationDeviceStateSummary,
        )

        return self.properties.get(
            "deviceConfigurationDeviceStateSummaries",
            DeviceConfigurationDeviceStateSummary(
                self.context, ResourcePath("deviceConfigurationDeviceStateSummaries", self.resource_path)
            ),
        )

    @property
    def device_configurations(self) -> EntityCollection[DeviceConfiguration]:
        """Gets the deviceConfigurations property"""
        from office365.intune.devices.configurations.configuration import (
            DeviceConfiguration,
        )

        return self.properties.get(
            "deviceConfigurations",
            EntityCollection[DeviceConfiguration](
                self.context, DeviceConfiguration, ResourcePath("deviceConfigurations", self.resource_path)
            ),
        )

    @property
    def ios_update_statuses(self) -> EntityCollection[IosUpdateDeviceStatus]:
        """Gets the iosUpdateStatuses property"""
        from office365.intune.devices.management.ios_update_device_status import IosUpdateDeviceStatus

        return self.properties.get(
            "iosUpdateStatuses",
            EntityCollection[IosUpdateDeviceStatus](
                self.context, IosUpdateDeviceStatus, ResourcePath("iosUpdateStatuses", self.resource_path)
            ),
        )

    @property
    def software_update_status_summary(self) -> SoftwareUpdateStatusSummary:
        """Gets the softwareUpdateStatusSummary property"""
        from office365.intune.devices.management.software_update_status_summary import (
            SoftwareUpdateStatusSummary,
        )

        return self.properties.get(
            "softwareUpdateStatusSummary",
            SoftwareUpdateStatusSummary(self.context, ResourcePath("softwareUpdateStatusSummary", self.resource_path)),
        )

    @property
    def compliance_management_partners(self) -> EntityCollection[ComplianceManagementPartner]:
        """Gets the complianceManagementPartners property"""
        from office365.intune.devices.compliance.management_partner import (
            ComplianceManagementPartner,
        )

        return self.properties.get(
            "complianceManagementPartners",
            EntityCollection[ComplianceManagementPartner](
                self.context,
                ComplianceManagementPartner,
                ResourcePath("complianceManagementPartners", self.resource_path),
            ),
        )

    @property
    def conditional_access_settings(self) -> OnPremisesConditionalAccessSettings:
        """Gets the conditionalAccessSettings property"""
        from office365.intune.devices.management.on_premises_conditional_access_settings import (
            OnPremisesConditionalAccessSettings,
        )

        return self.properties.get(
            "conditionalAccessSettings",
            OnPremisesConditionalAccessSettings(
                self.context, ResourcePath("conditionalAccessSettings", self.resource_path)
            ),
        )

    @property
    def device_management_partners(self) -> EntityCollection[DeviceManagementPartner]:
        """Gets the deviceManagementPartners property"""
        from office365.intune.devices.management_partner import DeviceManagementPartner

        return self.properties.get(
            "deviceManagementPartners",
            EntityCollection[DeviceManagementPartner](
                self.context, DeviceManagementPartner, ResourcePath("deviceManagementPartners", self.resource_path)
            ),
        )

    @property
    def exchange_connectors(self) -> EntityCollection[DeviceManagementExchangeConnector]:
        """Gets the exchangeConnectors property"""
        from office365.intune.devices.management_exchange_connector import (
            DeviceManagementExchangeConnector,
        )

        return self.properties.get(
            "exchangeConnectors",
            EntityCollection[DeviceManagementExchangeConnector](
                self.context, DeviceManagementExchangeConnector, ResourcePath("exchangeConnectors", self.resource_path)
            ),
        )

    @property
    def mobile_threat_defense_connectors(self) -> EntityCollection[MobileThreatDefenseConnector]:
        """Gets the mobileThreatDefenseConnectors property"""
        from office365.intune.devices.management.mobile_threat_defense_connector import (
            MobileThreatDefenseConnector,
        )

        return self.properties.get(
            "mobileThreatDefenseConnectors",
            EntityCollection[MobileThreatDefenseConnector](
                self.context,
                MobileThreatDefenseConnector,
                ResourcePath("mobileThreatDefenseConnectors", self.resource_path),
            ),
        )

    @property
    def apple_push_notification_certificate(self) -> ApplePushNotificationCertificate:
        """Gets the applePushNotificationCertificate property"""
        from office365.intune.devices.management.apple_push_notification_certificate import (
            ApplePushNotificationCertificate,
        )

        return self.properties.get(
            "applePushNotificationCertificate",
            ApplePushNotificationCertificate(
                self.context, ResourcePath("applePushNotificationCertificate", self.resource_path)
            ),
        )

    @property
    def detected_apps(self) -> EntityCollection[DetectedApp]:
        """Gets the detectedApps property"""
        from office365.intune.devices.management.detected_app import DetectedApp

        return self.properties.get(
            "detectedApps",
            EntityCollection[DetectedApp](self.context, DetectedApp, ResourcePath("detectedApps", self.resource_path)),
        )

    @property
    def managed_device_overview(self) -> ManagedDeviceOverview:
        """Gets the managedDeviceOverview property"""
        from office365.intune.devices.management.managed.device_overview import ManagedDeviceOverview

        return self.properties.get(
            "managedDeviceOverview",
            ManagedDeviceOverview(self.context, ResourcePath("managedDeviceOverview", self.resource_path)),
        )

    @property
    def mobile_app_troubleshooting_events(self) -> EntityCollection[MobileAppTroubleshootingEvent]:
        """Gets the mobileAppTroubleshootingEvents property"""
        from office365.intune.devices.management.mobileapps.mobile_app_troubleshooting_event import (
            MobileAppTroubleshootingEvent,
        )

        return self.properties.get(
            "mobileAppTroubleshootingEvents",
            EntityCollection[MobileAppTroubleshootingEvent](
                self.context,
                MobileAppTroubleshootingEvent,
                ResourcePath("mobileAppTroubleshootingEvents", self.resource_path),
            ),
        )

    @property
    def user_experience_analytics_app_health_application_performance(
        self,
    ) -> EntityCollection[UserExperienceAnalyticsAppHealthApplicationPerformance]:
        """Gets the userExperienceAnalyticsAppHealthApplicationPerformance property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_app_health_application_performance import (  # noqa: E501
            UserExperienceAnalyticsAppHealthApplicationPerformance,
        )

        return self.properties.get(
            "userExperienceAnalyticsAppHealthApplicationPerformance",
            EntityCollection[UserExperienceAnalyticsAppHealthApplicationPerformance](
                self.context,
                UserExperienceAnalyticsAppHealthApplicationPerformance,
                ResourcePath("userExperienceAnalyticsAppHealthApplicationPerformance", self.resource_path),
            ),
        )

    @property
    def user_experience_analytics_app_health_application_performance_by_app_version_details(
        self,
    ) -> EntityCollection[UserExperienceAnalyticsAppHealthAppPerformanceByAppVersionDetails]:
        """Gets the userExperienceAnalyticsAppHealthApplicationPerformanceByAppVersionDetails property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_app_health_app_performance_by_app_version_details import (  # noqa: E501
            UserExperienceAnalyticsAppHealthAppPerformanceByAppVersionDetails,
        )

        return self.properties.get(
            "userExperienceAnalyticsAppHealthApplicationPerformanceByAppVersionDetails",
            EntityCollection[UserExperienceAnalyticsAppHealthAppPerformanceByAppVersionDetails](
                self.context,
                UserExperienceAnalyticsAppHealthAppPerformanceByAppVersionDetails,
                ResourcePath(
                    "userExperienceAnalyticsAppHealthApplicationPerformanceByAppVersionDetails", self.resource_path
                ),
            ),
        )

    @property
    def user_experience_analytics_app_health_application_performance_by_app_version_device_id(
        self,
    ) -> EntityCollection[UserExperienceAnalyticsAppHealthAppPerformanceByAppVersionDeviceId]:
        """Gets the userExperienceAnalyticsAppHealthApplicationPerformanceByAppVersionDeviceId property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_app_health_app_performance_by_app_version_device_id import (  # noqa: E501
            UserExperienceAnalyticsAppHealthAppPerformanceByAppVersionDeviceId,
        )

        return self.properties.get(
            "userExperienceAnalyticsAppHealthApplicationPerformanceByAppVersionDeviceId",
            EntityCollection[UserExperienceAnalyticsAppHealthAppPerformanceByAppVersionDeviceId](
                self.context,
                UserExperienceAnalyticsAppHealthAppPerformanceByAppVersionDeviceId,
                ResourcePath(
                    "userExperienceAnalyticsAppHealthApplicationPerformanceByAppVersionDeviceId", self.resource_path
                ),
            ),
        )

    @property
    def user_experience_analytics_app_health_application_performance_by_os_version(
        self,
    ) -> EntityCollection[UserExperienceAnalyticsAppHealthAppPerformanceByOSVersion]:
        """Gets the userExperienceAnalyticsAppHealthApplicationPerformanceByOSVersion property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_app_health_app_performance_by_os_version import (  # noqa: E501
            UserExperienceAnalyticsAppHealthAppPerformanceByOSVersion,
        )

        return self.properties.get(
            "userExperienceAnalyticsAppHealthApplicationPerformanceByOSVersion",
            EntityCollection[UserExperienceAnalyticsAppHealthAppPerformanceByOSVersion](
                self.context,
                UserExperienceAnalyticsAppHealthAppPerformanceByOSVersion,
                ResourcePath("userExperienceAnalyticsAppHealthApplicationPerformanceByOSVersion", self.resource_path),
            ),
        )

    @property
    def user_experience_analytics_app_health_device_model_performance(
        self,
    ) -> EntityCollection[UserExperienceAnalyticsAppHealthDeviceModelPerformance]:
        """Gets the userExperienceAnalyticsAppHealthDeviceModelPerformance property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_app_health_device_model_performance import (  # noqa: E501
            UserExperienceAnalyticsAppHealthDeviceModelPerformance,
        )

        return self.properties.get(
            "userExperienceAnalyticsAppHealthDeviceModelPerformance",
            EntityCollection[UserExperienceAnalyticsAppHealthDeviceModelPerformance](
                self.context,
                UserExperienceAnalyticsAppHealthDeviceModelPerformance,
                ResourcePath("userExperienceAnalyticsAppHealthDeviceModelPerformance", self.resource_path),
            ),
        )

    @property
    def user_experience_analytics_app_health_device_performance(
        self,
    ) -> EntityCollection[UserExperienceAnalyticsAppHealthDevicePerformance]:
        """Gets the userExperienceAnalyticsAppHealthDevicePerformance property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_app_health_device_performance import (  # noqa: E501
            UserExperienceAnalyticsAppHealthDevicePerformance,
        )

        return self.properties.get(
            "userExperienceAnalyticsAppHealthDevicePerformance",
            EntityCollection[UserExperienceAnalyticsAppHealthDevicePerformance](
                self.context,
                UserExperienceAnalyticsAppHealthDevicePerformance,
                ResourcePath("userExperienceAnalyticsAppHealthDevicePerformance", self.resource_path),
            ),
        )

    @property
    def user_experience_analytics_app_health_device_performance_details(
        self,
    ) -> EntityCollection[UserExperienceAnalyticsAppHealthDevicePerformanceDetails]:
        """Gets the userExperienceAnalyticsAppHealthDevicePerformanceDetails property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_app_health_device_performance_details import (  # noqa: E501
            UserExperienceAnalyticsAppHealthDevicePerformanceDetails,
        )

        return self.properties.get(
            "userExperienceAnalyticsAppHealthDevicePerformanceDetails",
            EntityCollection[UserExperienceAnalyticsAppHealthDevicePerformanceDetails](
                self.context,
                UserExperienceAnalyticsAppHealthDevicePerformanceDetails,
                ResourcePath("userExperienceAnalyticsAppHealthDevicePerformanceDetails", self.resource_path),
            ),
        )

    @property
    def user_experience_analytics_app_health_os_version_performance(
        self,
    ) -> EntityCollection[UserExperienceAnalyticsAppHealthOSVersionPerformance]:
        """Gets the userExperienceAnalyticsAppHealthOSVersionPerformance property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_app_health_os_version_performance import (  # noqa: E501
            UserExperienceAnalyticsAppHealthOSVersionPerformance,
        )

        return self.properties.get(
            "userExperienceAnalyticsAppHealthOSVersionPerformance",
            EntityCollection[UserExperienceAnalyticsAppHealthOSVersionPerformance](
                self.context,
                UserExperienceAnalyticsAppHealthOSVersionPerformance,
                ResourcePath("userExperienceAnalyticsAppHealthOSVersionPerformance", self.resource_path),
            ),
        )

    @property
    def user_experience_analytics_app_health_overview(self) -> UserExperienceAnalyticsCategory:
        """Gets the userExperienceAnalyticsAppHealthOverview property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_category import (
            UserExperienceAnalyticsCategory,
        )

        return self.properties.get(
            "userExperienceAnalyticsAppHealthOverview",
            UserExperienceAnalyticsCategory(
                self.context, ResourcePath("userExperienceAnalyticsAppHealthOverview", self.resource_path)
            ),
        )

    @property
    def user_experience_analytics_baselines(self) -> EntityCollection[UserExperienceAnalyticsBaseline]:
        """Gets the userExperienceAnalyticsBaselines property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_baseline import (
            UserExperienceAnalyticsBaseline,
        )

        return self.properties.get(
            "userExperienceAnalyticsBaselines",
            EntityCollection[UserExperienceAnalyticsBaseline](
                self.context,
                UserExperienceAnalyticsBaseline,
                ResourcePath("userExperienceAnalyticsBaselines", self.resource_path),
            ),
        )

    @property
    def user_experience_analytics_categories(self) -> EntityCollection[UserExperienceAnalyticsCategory]:
        """Gets the userExperienceAnalyticsCategories property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_category import (
            UserExperienceAnalyticsCategory,
        )

        return self.properties.get(
            "userExperienceAnalyticsCategories",
            EntityCollection[UserExperienceAnalyticsCategory](
                self.context,
                UserExperienceAnalyticsCategory,
                ResourcePath("userExperienceAnalyticsCategories", self.resource_path),
            ),
        )

    @property
    def user_experience_analytics_device_performance(self) -> EntityCollection[UserExperienceAnalyticsDevicePerformance]:
        """Gets the userExperienceAnalyticsDevicePerformance property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_device_performance import (  # noqa: E501
            UserExperienceAnalyticsDevicePerformance,
        )

        return self.properties.get(
            "userExperienceAnalyticsDevicePerformance",
            EntityCollection[UserExperienceAnalyticsDevicePerformance](
                self.context,
                UserExperienceAnalyticsDevicePerformance,
                ResourcePath("userExperienceAnalyticsDevicePerformance", self.resource_path),
            ),
        )

    @property
    def user_experience_analytics_device_scores(self) -> EntityCollection[UserExperienceAnalyticsDeviceScores]:
        """Gets the userExperienceAnalyticsDeviceScores property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_device_scores import (
            UserExperienceAnalyticsDeviceScores,
        )

        return self.properties.get(
            "userExperienceAnalyticsDeviceScores",
            EntityCollection[UserExperienceAnalyticsDeviceScores](
                self.context,
                UserExperienceAnalyticsDeviceScores,
                ResourcePath("userExperienceAnalyticsDeviceScores", self.resource_path),
            ),
        )

    @property
    def user_experience_analytics_device_startup_history(
        self,
    ) -> EntityCollection[UserExperienceAnalyticsDeviceStartupHistory]:
        """Gets the userExperienceAnalyticsDeviceStartupHistory property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_device_startup_history import (  # noqa: E501
            UserExperienceAnalyticsDeviceStartupHistory,
        )

        return self.properties.get(
            "userExperienceAnalyticsDeviceStartupHistory",
            EntityCollection[UserExperienceAnalyticsDeviceStartupHistory](
                self.context,
                UserExperienceAnalyticsDeviceStartupHistory,
                ResourcePath("userExperienceAnalyticsDeviceStartupHistory", self.resource_path),
            ),
        )

    @property
    def user_experience_analytics_device_startup_processes(
        self,
    ) -> EntityCollection[UserExperienceAnalyticsDeviceStartupProcess]:
        """Gets the userExperienceAnalyticsDeviceStartupProcesses property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_device_startup_process import (  # noqa: E501
            UserExperienceAnalyticsDeviceStartupProcess,
        )

        return self.properties.get(
            "userExperienceAnalyticsDeviceStartupProcesses",
            EntityCollection[UserExperienceAnalyticsDeviceStartupProcess](
                self.context,
                UserExperienceAnalyticsDeviceStartupProcess,
                ResourcePath("userExperienceAnalyticsDeviceStartupProcesses", self.resource_path),
            ),
        )

    @property
    def user_experience_analytics_device_startup_process_performance(
        self,
    ) -> EntityCollection[UserExperienceAnalyticsDeviceStartupProcessPerformance]:
        """Gets the userExperienceAnalyticsDeviceStartupProcessPerformance property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_device_startup_process_performance import (  # noqa: E501
            UserExperienceAnalyticsDeviceStartupProcessPerformance,
        )

        return self.properties.get(
            "userExperienceAnalyticsDeviceStartupProcessPerformance",
            EntityCollection[UserExperienceAnalyticsDeviceStartupProcessPerformance](
                self.context,
                UserExperienceAnalyticsDeviceStartupProcessPerformance,
                ResourcePath("userExperienceAnalyticsDeviceStartupProcessPerformance", self.resource_path),
            ),
        )

    @property
    def user_experience_analytics_metric_history(self) -> EntityCollection[UserExperienceAnalyticsMetricHistory]:
        """Gets the userExperienceAnalyticsMetricHistory property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_metric_history import (  # noqa: E501
            UserExperienceAnalyticsMetricHistory,
        )

        return self.properties.get(
            "userExperienceAnalyticsMetricHistory",
            EntityCollection[UserExperienceAnalyticsMetricHistory](
                self.context,
                UserExperienceAnalyticsMetricHistory,
                ResourcePath("userExperienceAnalyticsMetricHistory", self.resource_path),
            ),
        )

    @property
    def user_experience_analytics_model_scores(self) -> EntityCollection[UserExperienceAnalyticsModelScores]:
        """Gets the userExperienceAnalyticsModelScores property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_model_scores import (
            UserExperienceAnalyticsModelScores,
        )

        return self.properties.get(
            "userExperienceAnalyticsModelScores",
            EntityCollection[UserExperienceAnalyticsModelScores](
                self.context,
                UserExperienceAnalyticsModelScores,
                ResourcePath("userExperienceAnalyticsModelScores", self.resource_path),
            ),
        )

    @property
    def user_experience_analytics_overview(self) -> UserExperienceAnalyticsOverview:
        """Gets the userExperienceAnalyticsOverview property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_overview import (
            UserExperienceAnalyticsOverview,
        )

        return self.properties.get(
            "userExperienceAnalyticsOverview",
            UserExperienceAnalyticsOverview(
                self.context, ResourcePath("userExperienceAnalyticsOverview", self.resource_path)
            ),
        )

    @property
    def user_experience_analytics_score_history(self) -> EntityCollection[UserExperienceAnalyticsScoreHistory]:
        """Gets the userExperienceAnalyticsScoreHistory property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_score_history import (
            UserExperienceAnalyticsScoreHistory,
        )

        return self.properties.get(
            "userExperienceAnalyticsScoreHistory",
            EntityCollection[UserExperienceAnalyticsScoreHistory](
                self.context,
                UserExperienceAnalyticsScoreHistory,
                ResourcePath("userExperienceAnalyticsScoreHistory", self.resource_path),
            ),
        )

    @property
    def user_experience_analytics_work_from_anywhere_hardware_readiness_metric(
        self,
    ) -> UserExperienceAnalyticsWorkFromAnywhereHardwareReadinessMetric:
        """Gets the userExperienceAnalyticsWorkFromAnywhereHardwareReadinessMetric property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_work_from_anywhere_hardware_readiness_metric import (  # noqa: E501
            UserExperienceAnalyticsWorkFromAnywhereHardwareReadinessMetric,
        )

        return self.properties.get(
            "userExperienceAnalyticsWorkFromAnywhereHardwareReadinessMetric",
            UserExperienceAnalyticsWorkFromAnywhereHardwareReadinessMetric(
                self.context,
                ResourcePath("userExperienceAnalyticsWorkFromAnywhereHardwareReadinessMetric", self.resource_path),
            ),
        )

    @property
    def user_experience_analytics_work_from_anywhere_metrics(
        self,
    ) -> EntityCollection[UserExperienceAnalyticsWorkFromAnywhereMetric]:
        """Gets the userExperienceAnalyticsWorkFromAnywhereMetrics property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_work_from_anywhere_metric import (  # noqa: E501
            UserExperienceAnalyticsWorkFromAnywhereMetric,
        )

        return self.properties.get(
            "userExperienceAnalyticsWorkFromAnywhereMetrics",
            EntityCollection[UserExperienceAnalyticsWorkFromAnywhereMetric](
                self.context,
                UserExperienceAnalyticsWorkFromAnywhereMetric,
                ResourcePath("userExperienceAnalyticsWorkFromAnywhereMetrics", self.resource_path),
            ),
        )

    @property
    def user_experience_analytics_work_from_anywhere_model_performance(
        self,
    ) -> EntityCollection[UserExperienceAnalyticsWorkFromAnywhereModelPerformance]:
        """Gets the userExperienceAnalyticsWorkFromAnywhereModelPerformance property"""
        from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_work_from_anywhere_model_performance import (  # noqa: E501
            UserExperienceAnalyticsWorkFromAnywhereModelPerformance,
        )

        return self.properties.get(
            "userExperienceAnalyticsWorkFromAnywhereModelPerformance",
            EntityCollection[UserExperienceAnalyticsWorkFromAnywhereModelPerformance](
                self.context,
                UserExperienceAnalyticsWorkFromAnywhereModelPerformance,
                ResourcePath("userExperienceAnalyticsWorkFromAnywhereModelPerformance", self.resource_path),
            ),
        )

    @property
    def windows_malware_information(self) -> EntityCollection[WindowsMalwareInformation]:
        """Gets the windowsMalwareInformation property"""
        from office365.intune.devices.management.windowsmalware.windows_malware_information import (
            WindowsMalwareInformation,
        )

        return self.properties.get(
            "windowsMalwareInformation",
            EntityCollection[WindowsMalwareInformation](
                self.context, WindowsMalwareInformation, ResourcePath("windowsMalwareInformation", self.resource_path)
            ),
        )

    @property
    def imported_windows_autopilot_device_identities(self) -> EntityCollection[ImportedWindowsAutopilotDeviceIdentity]:
        """Gets the importedWindowsAutopilotDeviceIdentities property"""
        from office365.intune.devices.management.imported_windows_autopilot_device_identity import (
            ImportedWindowsAutopilotDeviceIdentity,
        )

        return self.properties.get(
            "importedWindowsAutopilotDeviceIdentities",
            EntityCollection[ImportedWindowsAutopilotDeviceIdentity](
                self.context,
                ImportedWindowsAutopilotDeviceIdentity,
                ResourcePath("importedWindowsAutopilotDeviceIdentities", self.resource_path),
            ),
        )

    @property
    def windows_autopilot_device_identities(self) -> EntityCollection[WindowsAutopilotDeviceIdentity]:
        """Gets the windowsAutopilotDeviceIdentities property"""
        from office365.intune.devices.management.windows_autopilot_device_identity import (
            WindowsAutopilotDeviceIdentity,
        )

        return self.properties.get(
            "windowsAutopilotDeviceIdentities",
            EntityCollection[WindowsAutopilotDeviceIdentity](
                self.context,
                WindowsAutopilotDeviceIdentity,
                ResourcePath("windowsAutopilotDeviceIdentities", self.resource_path),
            ),
        )

    @property
    def notification_message_templates(self) -> EntityCollection[NotificationMessageTemplate]:
        """Gets the notificationMessageTemplates property"""
        from office365.intune.devices.management.notification_message_template import (
            NotificationMessageTemplate,
        )

        return self.properties.get(
            "notificationMessageTemplates",
            EntityCollection[NotificationMessageTemplate](
                self.context,
                NotificationMessageTemplate,
                ResourcePath("notificationMessageTemplates", self.resource_path),
            ),
        )

    @property
    def resource_operations(self) -> EntityCollection[ResourceOperation]:
        """Gets the resourceOperations property"""
        from office365.intune.devices.management.resource_operation import (
            ResourceOperation,
        )

        return self.properties.get(
            "resourceOperations",
            EntityCollection[ResourceOperation](
                self.context, ResourceOperation, ResourcePath("resourceOperations", self.resource_path)
            ),
        )

    @property
    def role_assignments(self) -> EntityCollection[DeviceAndAppManagementRoleAssignment]:
        """Gets the roleAssignments property"""
        from office365.intune.devices.and_app_management_role_assignment import (
            DeviceAndAppManagementRoleAssignment,
        )

        return self.properties.get(
            "roleAssignments",
            EntityCollection[DeviceAndAppManagementRoleAssignment](
                self.context, DeviceAndAppManagementRoleAssignment, ResourcePath("roleAssignments", self.resource_path)
            ),
        )

    @property
    def role_definitions(self) -> EntityCollection[RoleDefinition]:
        """Gets the roleDefinitions property"""
        from office365.common.role_definition import RoleDefinition

        return self.properties.get(
            "roleDefinitions",
            EntityCollection[RoleDefinition](
                self.context, RoleDefinition, ResourcePath("roleDefinitions", self.resource_path)
            ),
        )

    @property
    def remote_assistance_partners(self) -> EntityCollection[RemoteAssistancePartner]:
        """Gets the remoteAssistancePartners property"""
        from office365.intune.devices.management.remoteassistance.partner import (
            RemoteAssistancePartner,
        )

        return self.properties.get(
            "remoteAssistancePartners",
            EntityCollection[RemoteAssistancePartner](
                self.context, RemoteAssistancePartner, ResourcePath("remoteAssistancePartners", self.resource_path)
            ),
        )

    @property
    def troubleshooting_events(self) -> EntityCollection[DeviceManagementTroubleshootingEvent]:
        """Gets the troubleshootingEvents property"""
        from office365.intune.devices.management_troubleshooting_event import (
            DeviceManagementTroubleshootingEvent,
        )

        return self.properties.get(
            "troubleshootingEvents",
            EntityCollection[DeviceManagementTroubleshootingEvent](
                self.context,
                DeviceManagementTroubleshootingEvent,
                ResourcePath("troubleshootingEvents", self.resource_path),
            ),
        )

    @property
    def windows_information_protection_app_learning_summaries(
        self,
    ) -> EntityCollection[WindowsInformationProtectionAppLearningSummary]:
        """Gets the windowsInformationProtectionAppLearningSummaries property"""
        from office365.intune.devices.management.windows_information_protection_app_learning_summary import (
            WindowsInformationProtectionAppLearningSummary,
        )

        return self.properties.get(
            "windowsInformationProtectionAppLearningSummaries",
            EntityCollection[WindowsInformationProtectionAppLearningSummary](
                self.context,
                WindowsInformationProtectionAppLearningSummary,
                ResourcePath("windowsInformationProtectionAppLearningSummaries", self.resource_path),
            ),
        )

    @property
    def windows_information_protection_network_learning_summaries(
        self,
    ) -> EntityCollection[WindowsInformationProtectionNetworkLearningSummary]:
        """Gets the windowsInformationProtectionNetworkLearningSummaries property"""
        from office365.intune.devices.management.windows_information_protection_network_learning_summary import (
            WindowsInformationProtectionNetworkLearningSummary,
        )

        return self.properties.get(
            "windowsInformationProtectionNetworkLearningSummaries",
            EntityCollection[WindowsInformationProtectionNetworkLearningSummary](
                self.context,
                WindowsInformationProtectionNetworkLearningSummary,
                ResourcePath("windowsInformationProtectionNetworkLearningSummaries", self.resource_path),
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DeviceManagement"
