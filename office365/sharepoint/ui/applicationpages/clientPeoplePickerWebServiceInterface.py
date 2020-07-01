from office365.runtime.client_result import ClientResult
from office365.runtime.queries.serviceOperationQuery import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.ui.applicationpages.clientPeoplePickerQueryParameters import ClientPeoplePickerQueryParameters


class ClientPeoplePickerWebServiceInterface(BaseEntity):

    def __init__(self, context):
        super().__init__(context)

    @staticmethod
    def client_people_picker_resolve_user(context, queryParams):
        """
        Resolves the principals to a string of JSON representing users in people picker format.


        :param ClientPeoplePickerQueryParameters queryParams: Specifies the properties of a principal query.
        :param office365.sharepoint.client_context.ClientContext context:

        """
        result = ClientResult(str)
        svc = ClientPeoplePickerWebServiceInterface(context)
        qry = ServiceOperationQuery(svc, "ClientPeoplePickerResolveUser", None, queryParams, "queryParams", result)
        qry.static = True
        context.add_query(qry)

        def _process_result(return_value):
            result.value = "[{0}]".format(return_value.value)

        context.afterExecuteOnce += _process_result
        return result

    @property
    def entity_type_name(self):
        return "SP.UI.ApplicationPages.ClientPeoplePickerWebServiceInterface"
