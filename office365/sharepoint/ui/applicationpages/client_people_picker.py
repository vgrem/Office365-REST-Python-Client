from office365.runtime.client_result import ClientResult
from office365.runtime.client_value import ClientValue
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.principal.principal_source import PrincipalSource
from office365.sharepoint.principal.principal_type import PrincipalType
from office365.sharepoint.ui.applicationpages.picker_entity_types import PickerEntityInformation, \
    PickerEntityInformationRequest


class PeoplePickerQuerySettings(ClientValue):
    """Represents additional settings for the principal query."""
    pass


class ClientPeoplePickerQueryParameters(ClientValue):

    def __init__(self, query_string, allowEmailAddresses=True, allowMultipleEntities=True, allowOnlyEmailAddresses=False,
                 allUrlZones=False, enabledClaimProviders=None, forceClaims=False, maximumEntitySuggestions=1,
                 principalSource=PrincipalSource.All, principalType=PrincipalType.All, urlZone=0,
                 urlZoneSpecified=False, sharepoint_group_id=0):
        """
        Specifies the properties of a principal query

        :type int urlZone: Specifies a location in the topology of the farm for the principal query.
        :param int sharepoint_group_id: specifies a group containing allowed principals to be used in the principal query.
        :param str query_string: Specifies the value to be used in the principal query.
        :param int principalType: Specifies the type to be used in the principal query.
        :param int principalSource: Specifies the source to be used in the principal query.
        :param int maximumEntitySuggestions: Specifies the maximum number of principals to be returned by the
        principal query.
        :param bool forceClaims: Specifies whether the principal query SHOULD be handled by claims providers.
        :param bool enabledClaimProviders: Specifies the claims providers to be used in the principal query.
        :param bool allUrlZones: Specifies whether the principal query will search all locations in the topology
        of the farm.
        :param bool allowOnlyEmailAddresses: Specifies whether to allow the picker to resolve only email addresses as
        valid entities. This property is only used when AllowEmailAddresses (section 3.2.5.217.1.1.1) is set to True.
        Otherwise it is ignored.
        :param bool allowMultipleEntities: Specifies whether the principal query allows multiple values.
        :param bool allowEmailAddresses: Specifies whether the principal query can return a resolved principal
        matching an unverified e-mail address when unable to resolve to a known principal.
        """
        super(ClientPeoplePickerQueryParameters, self).__init__()
        self.QueryString = query_string
        self.AllowEmailAddresses = allowEmailAddresses
        self.AllowMultipleEntities = allowMultipleEntities
        self.AllowOnlyEmailAddresses = allowOnlyEmailAddresses
        self.AllUrlZones = allUrlZones
        self.EnabledClaimProviders = enabledClaimProviders
        self.ForceClaims = forceClaims
        self.MaximumEntitySuggestions = maximumEntitySuggestions
        self.PrincipalSource = principalSource
        self.PrincipalType = principalType
        self.UrlZone = urlZone
        self.UrlZoneSpecified = urlZoneSpecified
        self.SharePointGroupID = sharepoint_group_id

    @property
    def entity_type_name(self):
        return "SP.UI.ApplicationPages.ClientPeoplePickerQueryParameters"


class ClientPeoplePickerWebServiceInterface(BaseEntity):
    """Specifies an interface that can be used to query principals."""

    def __init__(self, context):
        super(ClientPeoplePickerWebServiceInterface, self).__init__(context)

    @staticmethod
    def get_search_results(context, searchPattern, providerID=None, hierarchyNodeID=None, entityTypes=None):
        """
        :type context: office365.sharepoint.client_context.ClientContext
        :type searchPattern: str
        :type providerID: str
        :type hierarchyNodeID: str
        :type entityTypes: str
        """
        result = ClientResult(context)
        payload = {
            "searchPattern": searchPattern,
            "providerID": providerID,
            "hierarchyNodeID": hierarchyNodeID,
            "entityTypes": entityTypes
        }
        svc = ClientPeoplePickerWebServiceInterface(context)
        qry = ServiceOperationQuery(svc, "GetSearchResults", None, payload, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    @staticmethod
    def client_people_picker_resolve_user(context, query_params, on_resolved=None):
        """
        Resolves the principals to a string of JSON representing users in people picker format.


        :param (str) -> None on_resolved: resolved event
        :param ClientPeoplePickerQueryParameters query_params: Specifies the properties of a principal query.
        :param office365.sharepoint.client_context.ClientContext context:

        """
        result = ClientResult(context)
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
