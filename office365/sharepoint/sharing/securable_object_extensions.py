from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.sharing.information import SharingInformation
from office365.sharepoint.sharing.information_request import SharingInformationRequest


class SecurableObjectExtensions(BaseEntity):

    @staticmethod
    def get_sharing_information(context):
        """
        Gets the sharing information for a list item.

        :param office365.sharepoint.client_context.ClientContext context: Client context
        """
        return_type = SharingInformation(context)
        request = SharingInformationRequest()
        binding_type = SecurableObjectExtensions(context)
        qry = ServiceOperationQuery(binding_type, "GetSharingInformation", None, request, None, return_type, True)
        context.add_query(qry)
        return return_type

    @property
    def entity_type_name(self):
        return "SP.Sharing.SecurableObjectExtensions"
