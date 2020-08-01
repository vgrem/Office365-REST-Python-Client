from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity


class ClientPeoplePickerWebServiceInterface(BaseEntity):

    def __init__(self, context):
        super().__init__(context)

    @staticmethod
    def client_people_picker_resolve_user(context, query_params, on_resolved=None):
        """
        Resolves the principals to a string of JSON representing users in people picker format.


        :param (str) -> None on_resolved: resolved event
        :param ClientPeoplePickerQueryParameters query_params: Specifies the properties of a principal query.
        :param office365.sharepoint.client_context.ClientContext context:

        """
        result = ClientResult(str)
        svc = ClientPeoplePickerWebServiceInterface(context)
        qry = ServiceOperationQuery(svc, "ClientPeoplePickerResolveUser", None, query_params, "queryParams", result)
        qry.static = True
        context.add_query(qry)

        def _process_result(resp):
            result.value = "[{0}]".format(result.value)
            if callable(on_resolved):
                on_resolved(result.value)
        context.after_execute(_process_result)
        return result

    @property
    def entity_type_name(self):
        return "SP.UI.ApplicationPages.ClientPeoplePickerWebServiceInterface"
