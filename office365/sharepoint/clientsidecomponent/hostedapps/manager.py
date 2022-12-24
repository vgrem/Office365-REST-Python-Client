from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.clientsidecomponent.hostedapps.app import HostedApp


class HostedAppsManager(BaseEntity):

    def get_by_id(self, _id):
        """
        Gets an hosted app based on the Id.

        :param str _id: The Id of the hosted app to get.
        """
        return HostedApp(self.context, ServiceOperationPath("GetById", [_id], self.resource_path))

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.ClientSideComponent.HostedAppsManager"
