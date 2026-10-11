from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.b2b_registration_metrics import B2bRegistrationMetrics
    from office365.directory.b2b_sign_in_activity_metrics import B2BSignInActivityMetrics
    from office365.directory.multi_tenant_application_metrics import (
        MultiTenantApplicationMetrics,
    )
    from office365.partners.billing.metrics import BillingMetrics


class RelatedTenant(Entity):
    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def is_microsoft_infrastructure(self) -> Optional[bool]:
        """Gets the isMicrosoftInfrastructure property"""
        return self.properties.get("isMicrosoftInfrastructure", None)

    @property
    def app_b2_b_sign_in_activity_metrics(self) -> B2BSignInActivityMetrics:
        """Gets the appB2BSignInActivityMetrics property"""
        from office365.directory.b2b_sign_in_activity_metrics import (
            B2BSignInActivityMetrics,
        )

        return self.properties.get(
            "appB2BSignInActivityMetrics",
            B2BSignInActivityMetrics(self.context, ResourcePath("appB2BSignInActivityMetrics", self.resource_path)),
        )

    @property
    def b2_b_registration_metrics(self) -> B2bRegistrationMetrics:
        """Gets the b2BRegistrationMetrics property"""
        from office365.directory.b2b_registration_metrics import B2bRegistrationMetrics

        return self.properties.get(
            "b2BRegistrationMetrics",
            B2bRegistrationMetrics(self.context, ResourcePath("b2BRegistrationMetrics", self.resource_path)),
        )

    @property
    def b2_b_sign_in_activity_metrics(self) -> B2BSignInActivityMetrics:
        """Gets the b2BSignInActivityMetrics property"""
        from office365.directory.b2b_sign_in_activity_metrics import (
            B2BSignInActivityMetrics,
        )

        return self.properties.get(
            "b2BSignInActivityMetrics",
            B2BSignInActivityMetrics(self.context, ResourcePath("b2BSignInActivityMetrics", self.resource_path)),
        )

    @property
    def billing_metrics(self) -> BillingMetrics:
        """Gets the billingMetrics property"""
        from office365.partners.billing.metrics import BillingMetrics

        return self.properties.get(
            "billingMetrics", BillingMetrics(self.context, ResourcePath("billingMetrics", self.resource_path))
        )

    @property
    def multi_tenant_application_metrics(self) -> MultiTenantApplicationMetrics:
        """Gets the multiTenantApplicationMetrics property"""
        from office365.directory.multi_tenant_application_metrics import (
            MultiTenantApplicationMetrics,
        )

        return self.properties.get(
            "multiTenantApplicationMetrics",
            MultiTenantApplicationMetrics(
                self.context, ResourcePath("multiTenantApplicationMetrics", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.RelatedTenant"
