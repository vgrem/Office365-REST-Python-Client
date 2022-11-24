from office365.runtime.client_value import ClientValue


class SpecialTermResults(ClientValue):
    """The SpecialTermResults table contains best bets that apply to the search query. """

    @property
    def entity_type_name(self):
        return "Microsoft.Office.Server.Search.REST.SpecialTermResults"
