from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.search.refiner.refiner import Refiner


class RefinementResults(ClientValue):
    """
    The RefinementResults table contains refinement results that apply to the search query.
    """

    def __init__(self, refiners=None, properties=None):
        """
        :param list[Refiner] refiners:
        """
        self.Refiners = ClientValueCollection(Refiner, refiners)
        self.Properties = properties

    @property
    def entity_type_name(self):
        return "Microsoft.Office.Server.Search.REST.RefinementResults"
