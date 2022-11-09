from office365.runtime.client_value import ClientValue
from office365.sharepoint.activities.facets.rename import RenameFacet
from office365.sharepoint.activities.facets.sharing import SharingFacet


class ActionFacet(ClientValue):

    def __init__(self, rename=RenameFacet(), share=SharingFacet()):
        self.rename = rename
        self.share = share

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Activities.ActionFacet"
