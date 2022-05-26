from office365.runtime.client_value import ClientValue


class Sort(ClientValue):

    def __init__(self, property_name=None, direction=None):
        """
        :param str property_name:
        :param int direction:
        """
        self.Direction = direction
        self.Property = property_name

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Client.Search.Query.Sort"
