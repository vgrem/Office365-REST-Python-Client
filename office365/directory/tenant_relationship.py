from office365.directory.tenant_information import TenantInformation
from office365.entity import Entity
from office365.runtime.client_result import ClientResult
from office365.runtime.queries.function import FunctionQuery


class TenantRelationship(Entity):
    """Represent the various type of tenant relationships."""

    def find_tenant_information_by_domain_name(self, domain_name):
        """Given a domain name, search for a tenant and read its tenantInformation. You can use this API to
        validate tenant information and use their tenantId to configure cross-tenant access settings between you
        and the tenant.

        :param str domain_name: Primary domain name of an Azure AD tenant.
        """
        return_type = ClientResult(self.context, TenantInformation())
        params = {"domainName": domain_name}
        qry = FunctionQuery(self, "findTenantInformationByDomainName", params, return_type)
        self.context.add_query(qry)
        return return_type
