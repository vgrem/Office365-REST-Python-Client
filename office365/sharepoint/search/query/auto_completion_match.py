from office365.runtime.client_value import ClientValue


class QueryAutoCompletionMatch(ClientValue):
    """Represents one match in the Source for the Query"""

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Client.Search.Query.QueryAutoCompletionMatch"
