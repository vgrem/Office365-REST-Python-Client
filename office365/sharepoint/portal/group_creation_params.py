from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


class GroupCreationInformation(ClientValue):

    def __init__(self, display_name, alias, is_public, optional_params=None):
        super(GroupCreationInformation, self).__init__()
        if optional_params is None:
            optional_params = GroupCreationParams()
        self.displayName = display_name
        self.alias = alias
        self.isPublic = is_public
        self.optionalParams = optional_params

    @property
    def entity_type_name(self):
        return None


class GroupCreationParams(ClientValue):

    def __init__(self, classification="", description=""):
        super(GroupCreationParams, self).__init__()
        self.Classification = classification
        self.Description = description
        self.CreationOptions = ClientValueCollection(str)
        self.CreationOptions.add("SPSiteLanguage:1033")

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Portal.GroupCreationParams"
