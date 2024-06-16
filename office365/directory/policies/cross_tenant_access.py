from office365.directory.policies.base import PolicyBase
from office365.runtime.types.collections import StringCollection


class CrossTenantAccessPolicy(PolicyBase):
    """Represents the base policy in the directory for cross-tenant access settings."""

    @property
    def allowed_cloud_endpoints(self):
        """
        Used to specify which Microsoft clouds an organization would like to collaborate with. By default, this value
        is empty. Supported values for this field are: microsoftonline.com, microsoftonline.us,
        and partner.microsoftonline.cn.
        """
        return self.properties.get("allowedCloudEndpoints", StringCollection())
