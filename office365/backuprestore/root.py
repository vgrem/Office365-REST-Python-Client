from office365.backuprestore.service_status import ServiceStatus
from office365.directory.protection.policy.one_drive_for_business import (
    OneDriveForBusinessProtectionPolicy,
)
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_result import ClientResult
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery


class BackupRestoreRoot(Entity):
    """Represents the Microsoft 365 Backup Storage service in a tenant."""

    def enable(self, app_owner_tenant_id):
        """Enable the Microsoft 365 Backup Storage service for a tenant."""
        return_type = ClientResult(self.context, ServiceStatus())
        payload = {"appOwnerTenantId": app_owner_tenant_id}
        qry = ServiceOperationQuery(self, "enable", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def service_status(self):
        """Represents the tenant-level status of the Backup Storage service."""
        return self.properties.get("serviceStatus", ServiceStatus())

    @property
    def one_drive_for_business_protection_policies(self):
        """The list of OneDrive for Business restore sessions available in the tenant."""
        return self.properties.get(
            "oneDriveForBusinessProtectionPolicies",
            EntityCollection(
                self.context,
                OneDriveForBusinessProtectionPolicy,
                ResourcePath(
                    "oneDriveForBusinessProtectionPolicies", self.resource_path
                ),
            ),
        )

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "serviceStatus": self.service_status,
                "oneDriveForBusinessProtectionPolicies": self.one_drive_for_business_protection_policies,
            }
            default_value = property_mapping.get(name, None)
        return super(BackupRestoreRoot, self).get_property(name, default_value)
