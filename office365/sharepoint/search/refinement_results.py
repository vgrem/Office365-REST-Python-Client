from office365.runtime.client_value import ClientValue


class RefinementResults(ClientValue):
    """
    The RefinementResults table contains refinement results that apply to the search query.
    """

    @property
    def entity_type_name(self):
        return "Microsoft.Office.Server.Search.REST.RefinementResults"
