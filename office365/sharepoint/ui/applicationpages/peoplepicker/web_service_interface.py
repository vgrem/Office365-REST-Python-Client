from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.ui.applicationpages.peoplepicker.entity_information import PickerEntityInformation
from office365.sharepoint.ui.applicationpages.peoplepicker.entity_information_request import \
    PickerEntityInformationRequest
from office365.sharepoint.ui.applicationpages.peoplepicker.query_parameters import ClientPeoplePickerQueryParameters


class ClientPeoplePickerWebServiceInterface(BaseEntity):
    """Specifies an interface that can be used to query principals."""

    def __init__(self, context):
        super(ClientPeoplePickerWebServiceInterface, self).__init__(context)

    @staticmethod
    def get_search_results(context, search_pattern, provider_id=None, hierarchy_node_id=None, entity_types=None):
        """
        :type context: office365.sharepoint.client_context.ClientContext
        :type search_pattern: str
        :type provider_id: str
        :type hierarchy_node_id: str
        :type entity_types: str
        """
        result = ClientResult(context)
        payload = {
            "searchPattern": search_pattern,
            "providerID": provider_id,
            "hierarchyNodeID": hierarchy_node_id,
            "entityTypes": entity_types
        }
        svc = ClientPeoplePickerWebServiceInterface(context)
        qry = ServiceOperationQuery(svc, "GetSearchResults", None, payload, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    @staticmethod
    def client_people_picker_resolve_user(context, query_string):
        """
        Resolves the principals to a string of JSON representing users in people picker format.

        :param str query_string: Specifies the value to be used in the principal query.
        :param office365.sharepoint.client_context.ClientContext context:

        """
        return_type = ClientResult(context)
        svc = ClientPeoplePickerWebServiceInterface(context)
        query_params = ClientPeoplePickerQueryParameters(query_string=query_string)
        qry = ServiceOperationQuery(svc, "ClientPeoplePickerResolveUser", None, query_params, "queryParams", return_type)
        qry.static = True
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_picker_entity_information(context, email_address):
        """
        Gets information of the specified principal.

        :param office365.sharepoint.client_context.ClientContext context: SharePoint client context
        :param str email_address: Specifies the principal for which information is being requested.

        """
        request = PickerEntityInformationRequest(email_address=email_address)
        return_type = PickerEntityInformation(context)
        svc = ClientPeoplePickerWebServiceInterface(context)
        qry = ServiceOperationQuery(svc, "GetPickerEntityInformation",
                                    None,
                                    request,
                                    "entityInformationRequest",
                                    return_type)
        qry.static = True
        context.add_query(qry)
        return return_type

    @property
    def entity_type_name(self):
        return "SP.UI.ApplicationPages.ClientPeoplePickerWebServiceInterface"
