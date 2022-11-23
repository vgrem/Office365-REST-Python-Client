from office365.runtime.client_value import ClientValue


class QueryPropertyValue(ClientValue):
    """This object is used to store values of predefined types. The object MUST have a value set for only
    one of the property."""

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Client.Search.Query.QueryPropertyValue"
