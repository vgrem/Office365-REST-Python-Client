from office365.delta_collection import DeltaCollection
from office365.directory.serviceprincipals.service_principal import ServicePrincipal
from office365.runtime.paths.appid import AppIdPath


class ServicePrincipalCollection(DeltaCollection):
    """Service Principal's collection"""

    def __init__(self, context, resource_path=None):
        super(ServicePrincipalCollection, self).__init__(context, ServicePrincipal, resource_path)

    def add(self, app_id):
        """
        Create a new servicePrincipal object.

        :param str app_id: The unique identifier for the associated application
        :rtype: ServicePrincipal
        """
        return super(ServicePrincipalCollection, self).add(appId=app_id)

    def get_by_app_id(self, app_id):
        """Retrieves the service principal using appId.

        :param str app_id: appId is referred to as Application (Client) ID, respectively, in the Azure portal
        """
        return ServicePrincipal(self.context, AppIdPath(app_id, self.resource_path))
