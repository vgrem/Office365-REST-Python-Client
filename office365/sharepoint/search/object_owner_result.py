from office365.runtime.client_value import ClientValue


class SearchObjectOwnerResult(ClientValue):

    @property
    def entity_type_name(self):
        return "Microsoft.Office.Server.Search.REST.SearchObjectOwnerResult"
