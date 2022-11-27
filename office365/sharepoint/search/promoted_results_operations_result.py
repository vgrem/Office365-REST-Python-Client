from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.search.object_owner_result import SearchObjectOwnerResult
from office365.sharepoint.search.promoted_result_query_rule import PromotedResultQueryRule


class PromotedResultsOperationsResult(ClientValue):

    def __init__(self, result=None, object_owner=SearchObjectOwnerResult()):
        self.Result = ClientValueCollection(PromotedResultQueryRule, result)
        self.SearchObjectOwner = object_owner

    @property
    def entity_type_name(self):
        return "Microsoft.Office.Server.Search.REST.PromotedResultsOperationsResult"
