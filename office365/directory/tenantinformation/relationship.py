from __future__ import annotations

from typing import TYPE_CHECKING

from office365.directory.tenantinformation.information import TenantInformation
from office365.directory.tenantinformation.multi_organization import (
    MultiTenantOrganization,
)
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_result import ClientResult
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.directory.delegatedadmin.customer import DelegatedAdminCustomer
    from office365.directory.delegatedadmin.relationship import (
        DelegatedAdminRelationship,
    )


class TenantRelationship(Entity):
    """Represent the various type of tenant relationships."""

    def find_tenant_information_by_domain_name(self, domain_name: str) -> ClientResult[TenantInformation]:
        """Given a domain name, search for a tenant and read its tenantInformation. You can use this API to
        validate tenant information and use their tenantId to configure cross-tenant access settings between you
        and the tenant.

        Args:
            domain_name (str): Primary domain name of an Azure AD tenant.
        """
        return_type = ClientResult(self.context, TenantInformation())
        params = {"domainName": domain_name}
        qry = FunctionQuery(self, "findTenantInformationByDomainName", params, return_type)
        self.context.add_query(qry)
        return return_type

    def find_tenant_information_by_tenant_id(self, tenant_id: str) -> ClientResult[TenantInformation]:
        """Given a tenant ID, search for a tenant and read its tenantInformation. You can use this API to validate
        tenant information and use the tenantId to configure cross-tenant cross-tenant access settings between you
        and the tenant.

        Args:
            tenant_id (str): Unique tenant identifier of a Microsoft Entra tenant.
        """
        return_type = ClientResult(self.context, TenantInformation())
        params = {"tenantId": tenant_id}
        qry = FunctionQuery(self, "findTenantInformationByTenantId", params, return_type)
        self.context.add_query(qry)
        return return_type

    @odata(name="multiTenantOrganization")
    @property
    def multi_tenant_organization(self) -> MultiTenantOrganization:
        """Represents a setting to control people-related admin settings in the tenant."""
        return self.properties.get(
            "multiTenantOrganization",
            MultiTenantOrganization(
                self.context,
                ResourcePath("multiTenantOrganization", self.resource_path),
            ),
        )

    @property
    def delegated_admin_customers(self) -> EntityCollection[DelegatedAdminCustomer]:
        """Gets the delegatedAdminCustomers property"""
        from office365.directory.delegatedadmin.customer import DelegatedAdminCustomer

        return self.properties.get(
            "delegatedAdminCustomers",
            EntityCollection[DelegatedAdminCustomer](
                self.context, DelegatedAdminCustomer, ResourcePath("delegatedAdminCustomers", self.resource_path)
            ),
        )

    @property
    def delegated_admin_relationships(self) -> EntityCollection[DelegatedAdminRelationship]:
        """Gets the delegatedAdminRelationships property"""
        from office365.directory.delegatedadmin.relationship import (
            DelegatedAdminRelationship,
        )

        return self.properties.get(
            "delegatedAdminRelationships",
            EntityCollection[DelegatedAdminRelationship](
                self.context, DelegatedAdminRelationship, ResourcePath("delegatedAdminRelationships", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TenantRelationship"
