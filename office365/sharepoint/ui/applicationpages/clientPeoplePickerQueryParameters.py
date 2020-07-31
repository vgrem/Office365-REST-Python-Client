from office365.runtime.client_value import ClientValue
from office365.sharepoint.principal.principalSource import PrincipalSource
from office365.sharepoint.principal.principalType import PrincipalType


class ClientPeoplePickerQueryParameters(ClientValue):

    def __init__(self, queryString, allowEmailAddresses=True, allowMultipleEntities=True, allowOnlyEmailAddresses=False,
                 allUrlZones=False, enabledClaimProviders=None, forceClaims=False, maximumEntitySuggestions=1,
                 principalSource=PrincipalSource.All, principalType=PrincipalType.All, urlZone=0,
                 urlZoneSpecified=False, sharePointGroupID=0):
        """
        Specifies the properties of a principal query

        :type int urlZone: Specifies a location in the topology of the farm for the principal query.
        :param int sharePointGroupID: specifies a group containing allowed principals to be used in the principal query.
        :param str queryString: Specifies the value to be used in the principal query.
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
        super().__init__()
        self.QueryString = queryString
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
        self.SharePointGroupID = sharePointGroupID

    @property
    def entity_type_name(self):
        return "SP.UI.ApplicationPages.ClientPeoplePickerQueryParameters"
