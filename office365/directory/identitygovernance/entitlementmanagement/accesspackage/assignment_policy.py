from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.directory.identitygovernance.entitlementmanagement.accesspackage.question import (
    AccessPackageQuestion,
)
from office365.directory.identitygovernance.workflow.custom_extension_stage_setting import (
    CustomExtensionStageSetting,
)
from office365.directory.policies.allowedtargetscope import AllowedTargetScope
from office365.directory.subjectset import SubjectSet
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.identitygovernance.entitlementmanagement.accesspackage.assignment_approval_settings import (
        AccessPackageAssignmentApprovalSettings,
    )
    from office365.directory.identitygovernance.entitlementmanagement.accesspackage.assignment_requestor_settings import (  # noqa: E501
        AccessPackageAssignmentRequestorSettings,
    )
    from office365.directory.identitygovernance.entitlementmanagement.accesspackage.assignment_review_settings import (
        AccessPackageAssignmentReviewSettings,
    )
    from office365.directory.identitygovernance.entitlementmanagement.accesspackage.automatic_request_settings import (
        AccessPackageAutomaticRequestSettings,
    )
    from office365.directory.identitygovernance.entitlementmanagement.accesspackage.catalog import (
        AccessPackageCatalog,
    )
    from office365.directory.identitygovernance.entitlementmanagement.accesspackage.expiration_pattern import (
        ExpirationPattern,
    )
    from office365.directory.identitygovernance.entitlementmanagement.accesspackage.notification_settings import (
        AccessPackageNotificationSettings,
    )
    from office365.directory.identitygovernance.entitlementmanagement.accesspackage.package import (
        AccessPackage,
    )


class AccessPackageAssignmentPolicy(Entity):
    @property
    def allowed_target_scope(self) -> AllowedTargetScope:
        """Gets the allowedTargetScope property"""
        return self.properties.get("allowedTargetScope", AllowedTargetScope.notSpecified)

    @property
    def created_date_time(self) -> datetime:
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
    def modified_date_time(self) -> datetime:
        """Gets the modifiedDateTime property"""
        return self.properties.get("modifiedDateTime", datetime.min)

    @property
    def specific_allowed_targets(self) -> ClientValueCollection[SubjectSet]:
        """Gets the specificAllowedTargets property"""
        return self.properties.get("specificAllowedTargets", ClientValueCollection[SubjectSet](SubjectSet))

    @property
    def custom_extension_stage_settings(self) -> EntityCollection[CustomExtensionStageSetting]:
        """Gets the customExtensionStageSettings property"""
        return self.properties.get(
            "customExtensionStageSettings",
            EntityCollection[CustomExtensionStageSetting](
                self.context,
                CustomExtensionStageSetting,
                ResourcePath("customExtensionStageSettings", self.resource_path),
            ),
        )

    @property
    def questions(self) -> EntityCollection[AccessPackageQuestion]:
        """Gets the questions property"""
        return self.properties.get(
            "questions",
            EntityCollection[AccessPackageQuestion](
                self.context, AccessPackageQuestion, ResourcePath("questions", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AccessPackageAssignmentPolicy"

    @property
    def automatic_request_settings(self) -> AccessPackageAutomaticRequestSettings:
        """Gets the automaticRequestSettings property"""
        from office365.directory.identitygovernance.entitlementmanagement.accesspackage.automatic_request_settings import (  # noqa: E501
            AccessPackageAutomaticRequestSettings,
        )

        return self.properties.get("automaticRequestSettings", AccessPackageAutomaticRequestSettings())

    @property
    def expiration(self) -> ExpirationPattern:
        """Gets the expiration property"""
        from office365.directory.identitygovernance.entitlementmanagement.accesspackage.expiration_pattern import (
            ExpirationPattern,
        )

        return self.properties.get("expiration", ExpirationPattern())

    @property
    def notification_settings(self) -> AccessPackageNotificationSettings:
        """Gets the notificationSettings property"""
        from office365.directory.identitygovernance.entitlementmanagement.accesspackage.notification_settings import (
            AccessPackageNotificationSettings,
        )

        return self.properties.get("notificationSettings", AccessPackageNotificationSettings())

    @property
    def request_approval_settings(self) -> AccessPackageAssignmentApprovalSettings:
        """Gets the requestApprovalSettings property"""
        from office365.directory.identitygovernance.entitlementmanagement.accesspackage.assignment_approval_settings import (  # noqa: E501
            AccessPackageAssignmentApprovalSettings,
        )

        return self.properties.get("requestApprovalSettings", AccessPackageAssignmentApprovalSettings())

    @property
    def requestor_settings(self) -> AccessPackageAssignmentRequestorSettings:
        """Gets the requestorSettings property"""
        from office365.directory.identitygovernance.entitlementmanagement.accesspackage.assignment_requestor_settings import (  # noqa: E501
            AccessPackageAssignmentRequestorSettings,
        )

        return self.properties.get("requestorSettings", AccessPackageAssignmentRequestorSettings())

    @property
    def review_settings(self) -> AccessPackageAssignmentReviewSettings:
        """Gets the reviewSettings property"""
        from office365.directory.identitygovernance.entitlementmanagement.accesspackage.assignment_review_settings import (  # noqa: E501
            AccessPackageAssignmentReviewSettings,
        )

        return self.properties.get("reviewSettings", AccessPackageAssignmentReviewSettings())

    @property
    def access_package(self) -> AccessPackage:
        """Gets the accessPackage property"""
        from office365.directory.identitygovernance.entitlementmanagement.accesspackage.package import (
            AccessPackage,
        )

        return self.properties.get(
            "accessPackage", AccessPackage(self.context, ResourcePath("accessPackage", self.resource_path))
        )

    @property
    def catalog(self) -> AccessPackageCatalog:
        """Gets the catalog property"""
        from office365.directory.identitygovernance.entitlementmanagement.accesspackage.catalog import (
            AccessPackageCatalog,
        )

        return self.properties.get(
            "catalog", AccessPackageCatalog(self.context, ResourcePath("catalog", self.resource_path))
        )
