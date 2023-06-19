from office365.runtime.client_value import ClientValue


class SPAddinInstanceInfo(ClientValue):

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Marketplace.CorporateCuratedGallery.SPAddinInstanceInfo"
